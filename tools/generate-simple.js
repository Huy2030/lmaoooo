#!/usr/bin/env node
import puppeteer from 'puppeteer';
import fs from 'fs';
import path from 'path';
import http from 'http';
import https from 'https';
import { fileURLToPath } from 'url';
import sharp from 'sharp';
import { createWriteStream, createReadStream } from 'fs';
import { pipeline } from 'stream/promises';
import unzipper from 'unzipper';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const CONFIG = {
    assetsDir: process.env.ASSETS_DIR || './pack/assets',
    outputDir: process.env.OUTPUT_DIR || './staging/target/rp',
    iconSize: parseInt(process.env.ICON_SIZE) || 128,
    serverPort: 8765,
    downloadDir: process.env.DOWNLOAD_DIR || './downloads'
};

/**
 * Remove isolated pixels (noise) from PNG image
 * @param {Buffer} imageBuffer - Input image buffer
 * @param {number} minClusterSize - Minimum connected pixels to keep (default: 15)
 * @returns {Promise<Buffer>} - Cleaned image buffer
 */
async function removeIsolatedPixels(imageBuffer, minClusterSize = 15) {
    const image = sharp(imageBuffer);
    const { data, info } = await image.raw().toBuffer({ resolveWithObject: true });
    
    const width = info.width;
    const height = info.height;
    const channels = info.channels;
    
    // Create a copy of the data
    const pixels = new Uint8Array(data);
    const visited = new Array(width * height).fill(false);
    
    // Flood fill to find connected components
    function floodFill(startX, startY) {
        const cluster = [];
        const stack = [[startX, startY]];
        
        while (stack.length > 0) {
            const [x, y] = stack.pop();
            const idx = y * width + x;
            
            if (x < 0 || x >= width || y < 0 || y >= height) continue;
            if (visited[idx]) continue;
            
            const pixelIdx = idx * channels;
            const alpha = channels === 4 ? pixels[pixelIdx + 3] : 255;
            
            if (alpha === 0) continue; // Transparent pixel
            
            visited[idx] = true;
            cluster.push([x, y]);
            
            // Check 8 neighbors (including diagonals)
            stack.push([x + 1, y]);
            stack.push([x - 1, y]);
            stack.push([x, y + 1]);
            stack.push([x, y - 1]);
            stack.push([x + 1, y + 1]);
            stack.push([x + 1, y - 1]);
            stack.push([x - 1, y + 1]);
            stack.push([x - 1, y - 1]);
        }
        
        return cluster;
    }
    
    // Find all clusters
    const clusters = [];
    for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
            const idx = y * width + x;
            if (!visited[idx]) {
                const pixelIdx = idx * channels;
                const alpha = channels === 4 ? pixels[pixelIdx + 3] : 255;
                
                if (alpha > 0) {
                    const cluster = floodFill(x, y);
                    if (cluster.length > 0) {
                        clusters.push(cluster);
                    }
                }
            }
        }
    }
    
    // Remove small clusters (isolated pixels)
    for (const cluster of clusters) {
        if (cluster.length < minClusterSize) {
            for (const [x, y] of cluster) {
                const idx = (y * width + x) * channels;
                if (channels === 4) {
                    pixels[idx + 3] = 0; // Set alpha to 0 (transparent)
                } else {
                    // For RGB, set to transparent color
                    pixels[idx] = 0;
                    pixels[idx + 1] = 0;
                    pixels[idx + 2] = 0;
                }
            }
        }
    }
    
    // Convert back to image
    return sharp(pixels, {
        raw: {
            width: width,
            height: height,
            channels: channels
        }
    }).png().toBuffer();
}

/**
 * Download file from external URL
 * @param {string} url - URL to download from
 * @param {string} outputPath - Local path to save file
 * @returns {Promise<boolean>} - Success status
 */
async function downloadFile(url, outputPath) {
    return new Promise((resolve, reject) => {
        const protocol = url.startsWith('https') ? https : http;
        
        const outputDir = path.dirname(outputPath);
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }
        
        const file = createWriteStream(outputPath);
        
        const request = protocol.get(url, (response) => {
            if (response.statusCode === 302 || response.statusCode === 301) {
                // Handle redirect
                file.close();
                if (fs.existsSync(outputPath)) {
                    fs.unlinkSync(outputPath);
                }
                downloadFile(response.headers.location, outputPath)
                    .then(resolve)
                    .catch(reject);
                return;
            }
            
            if (response.statusCode !== 200) {
                file.close();
                if (fs.existsSync(outputPath)) {
                    fs.unlinkSync(outputPath);
                }
                reject(new Error(`Failed to download: ${response.statusCode}`));
                return;
            }
            
            const totalSize = parseInt(response.headers['content-length'], 10);
            let downloadedSize = 0;
            
            response.on('data', (chunk) => {
                downloadedSize += chunk.length;
            });
            
            response.pipe(file);
            
            file.on('finish', () => {
                file.close(() => {
                    // Wait a bit to ensure file is fully written to disk
                    setTimeout(() => {
                        resolve(true);
                    }, 500);
                });
            });
            
            file.on('error', (err) => {
                file.close();
                if (fs.existsSync(outputPath)) {
                    fs.unlinkSync(outputPath);
                }
                reject(err);
            });
        });
        
        request.on('error', (err) => {
            file.close();
            if (fs.existsSync(outputPath)) {
                fs.unlinkSync(outputPath);
            }
            reject(err);
        });
    });
}

/**
 * Extract ZIP file to destination folder (cross-platform)
 * @param {string} zipPath - Path to ZIP file
 * @param {string} destPath - Destination folder
 * @returns {Promise<boolean>}
 */
async function extractZip(zipPath, destPath) {
    if (!fs.existsSync(destPath)) {
        fs.mkdirSync(destPath, { recursive: true });
    }
    
    try {
        // Verify ZIP file exists and is readable
        if (!fs.existsSync(zipPath)) {
            throw new Error('ZIP file not found');
        }
        
        // Extract using unzipper
        const directory = await unzipper.Open.file(zipPath);
        await directory.extract({ path: destPath });
        
        return true;
    } catch (error) {
        return false;
    }
}

/**
 * Download and extract assets from Dropbox
 * @returns {Promise<boolean>}
 */
async function downloadAndExtractAssets() {
    const dropboxUrl = 'https://www.dropbox.com/scl/fi/tp80r9u82m25xy1pam8fc/minecraft.zip?rlkey=9xxc1t7kr1agp7gd5jnqfhvhp&st=h55le90t&dl=1';
    const zipPath = path.join(CONFIG.downloadDir, 'minecraft.zip');
    const assetsPath = path.resolve(__dirname, '../pack/assets');
    
    try {
        // Download ZIP file
        await downloadFile(dropboxUrl, zipPath);
        
        // Extract to assets folder
        const extracted = await extractZip(zipPath, assetsPath);
        
        if (extracted) {
            // Clean up ZIP file
            fs.unlinkSync(zipPath);
            return true;
        }
        
        return false;
    } catch (error) {
        return false;
    }
}

function findModelFiles(dir, fileList = [], assetsRoot = null) {
    // Determine assets root on first call
    if (!assetsRoot) {
        assetsRoot = dir;
    }
    
    const files = fs.readdirSync(dir);
    files.forEach(file => {
        const filePath = path.join(dir, file);
        if (fs.statSync(filePath).isDirectory()) {
            findModelFiles(filePath, fileList, assetsRoot);
        } else if (file.endsWith('.json')) {
            const baseName = file.replace('.json', '');
            
            // Get relative path from assets root
            const relativePath = path.relative(assetsRoot, filePath).replace(/\\/g, '/');
            
            // Skip non-model directories and files
            const skipPaths = [
                'minecraft/models/item/',
                'minecraft/models/block/',
                'minecraft/atlases/',
                'minecraft/font/',
                'minecraft/lang/',
                'minecraft/items/',
                'minecraft/optifine/',
                'minecraft/shaders/',
                'minecraft/blockstates/',
                'modelengine/'
            ];
            
            if (skipPaths.some(skipPath => relativePath.includes(skipPath))) {
                return;
            }
            
            // Skip specific files
            if (baseName === 'sounds' || relativePath.endsWith('minecraft/sounds.json')) {
                return;
            }
            
            // Skip animation states and variants (specific patterns only)
            const skipPatterns = [
                /bow_/,          // bow_0, bow_1, bow_2
                /crossbow_/,     // crossbow_0, crossbow_1, crossbow_2
                /shield_block/,       // shield_block, shield_blocking
                /_cosmetic$/,         // wings_cosmetic
                /_cosmetics$/,         // wings_cosmetic
                /_cosmetic_/,         // wings_cosmetic_self, wings_cosmetic_normal_2
                /_cosmetics_/,         // wings_cosmetic_self, wings_cosmetic_normal_2
                /_cosmetics/,         // wings_cosmetic_self, wings_cosmetic_normal_2
                /_self$/,             // any_self
                /staff_throwing/,     // staff_throwing variants
                /trident_throwing/,   // trident_throwing variants
            ];
            
            if (skipPatterns.some(p => p.test(baseName))) {
                return;
            }
            
            fileList.push(filePath);
        }
    });
    
    return fileList;
}

function findTextures(modelPath, modelData) {
    const textureFiles = {};
    const modelDir = path.dirname(modelPath);
    const assetsRoot = modelPath.split('assets')[0] + 'assets';
    
    if (!modelData.textures) return textureFiles;
    
    for (const [key, texturePath] of Object.entries(modelData.textures)) {
        // Skip texture references like "#1"
        if (texturePath.startsWith('#')) {
            continue;
        }
        
        let namespace = 'minecraft';
        let relativePath = texturePath;
        if (texturePath.includes(':')) {
            [namespace, relativePath] = texturePath.split(':');
        }
        
        const possiblePaths = [
            path.join(assetsRoot, namespace, 'textures', relativePath + '.png'),
            path.join(modelDir, '..', 'textures', relativePath + '.png'),
            path.join(assetsRoot, 'minecraft', 'textures', relativePath + '.png')
        ];
        
        for (const texPath of possiblePaths) {
            if (fs.existsSync(texPath)) {
                textureFiles[key] = texPath;
                break;
            }
        }
    }
    return textureFiles;
}

function createHTML(canvasSize = 128) {
    const buildJs = fs.readFileSync(path.join(__dirname, 'build.js'), 'utf-8');
    return `<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head><body>
<canvas id="canvas" width="${canvasSize}" height="${canvasSize}"></canvas>
<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js"}}</script>
<script type="module">
import * as THREE from 'three';
window.THREE = THREE;
${buildJs.replace('export class', 'window.MinecraftModelGeometry = class')}
const canvas = document.getElementById('canvas');
const scene = new THREE.Scene();

const frustumSize = 20;
const aspect = 1;
const camera = new THREE.OrthographicCamera(
    frustumSize * aspect / -2,
    frustumSize * aspect / 2,
    frustumSize / 2,
    frustumSize / -2,
    0.1,
    1000
);

camera.position.set(0, 0, 30);
camera.lookAt(0, 0, 0);

const renderer = new THREE.WebGLRenderer({canvas, alpha: true, preserveDrawingBuffer: true, antialias: false});
renderer.setSize(${canvasSize}, ${canvasSize});
renderer.setClearColor(0x000000, 0);
renderer.outputColorSpace = THREE.SRGBColorSpace;

const ambient = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambient);

const light1 = new THREE.DirectionalLight(0xffffff, 0.8);
light1.position.set(0.2, 1, 0.7);
scene.add(light1);

const light2 = new THREE.DirectionalLight(0xffffff, 0.4);
light2.position.set(-0.2, -1, -0.7);
scene.add(light2);

window.scene = scene;
window.camera = camera;
window.renderer = renderer;
window.ready = true;
</script>
</body></html>`;
}

function createServer(html) {
    const server = http.createServer((req, res) => {
        if (req.url === '/' || req.url === '/index.html') {
            res.writeHead(200, {'Content-Type': 'text/html'});
            res.end(html);
        } else {
            res.writeHead(404);
            res.end();
        }
    });
    
    return new Promise(resolve => {
        server.listen(CONFIG.serverPort, () => {
            resolve(server);
        });
    });
}

async function generateIcon(page, modelPath, outputPath) {
    try {
        const modelData = JSON.parse(fs.readFileSync(modelPath, 'utf-8'));
        
        // Check if this is a 2D flat model (generated item)
        const is2DModel = !modelData.elements && modelData.textures && (modelData.textures.layer0 || modelData.textures.layer1);
        
        if (is2DModel) {
            // Skip 2D flat models
            return false;
        }
        
        const textures = findTextures(modelPath, modelData);
        
        // Load textures as base64
        const textureData = {};
        
        // First pass: load actual texture files as base64
        for (const [key, texPath] of Object.entries(textures)) {
            try {
                const buffer = fs.readFileSync(texPath);
                const base64 = buffer.toString('base64');
                textureData[key] = `data:image/png;base64,${base64}`;
            } catch (e) {
                console.error(`Failed to read texture ${key}:`, e.message);
            }
        }
        
        // Second pass: resolve texture references like "#1"
        for (const [key, value] of Object.entries(modelData.textures || {})) {
            if (value.startsWith('#')) {
                const refKey = value.substring(1);
                if (textureData[refKey]) {
                    textureData[key] = textureData[refKey];
                }
            }
        }
        
        // Check if we should use particle texture for reference keys
        // If ANY numeric key (0, 1, 2...) is a reference (#name) and particle has real path, 
        // use particle ONLY for those reference keys (not for keys with real paths)
        if (modelData.textures && modelData.textures.particle && !modelData.textures.particle.startsWith('#')) {
            const numericKeys = Object.keys(modelData.textures).filter(k => /^\d+$/.test(k));
            
            // Check if at least one numeric key is a reference
            const hasRefKey = numericKeys.some(k => modelData.textures[k].startsWith('#'));
            
            if (hasRefKey && textureData.particle) {
                // Use particle texture ONLY for numeric keys that are references
                const particleData = textureData.particle;
                for (const key of numericKeys) {
                    if (modelData.textures[key].startsWith('#')) {
                        textureData[key] = particleData;
                    }
                }
            }
        }
        
        // Load textures in browser using createImageBitmap
        await page.evaluate(async (textureData) => {
            window.croppedTextures = {};
            
            for (const [key, dataUrl] of Object.entries(textureData)) {
                try {
                    const response = await fetch(dataUrl);
                    const blob = await response.blob();
                    const imageBitmap = await createImageBitmap(blob);
                    
                    // Check if animation frame (height > width) and crop if needed
                    let canvas = document.createElement('canvas');
                    if (imageBitmap.height > imageBitmap.width) {
                        const frameSize = imageBitmap.width;
                        canvas.width = frameSize;
                        canvas.height = frameSize;
                        const ctx = canvas.getContext('2d');
                        ctx.drawImage(imageBitmap, 0, 0, frameSize, frameSize, 0, 0, frameSize, frameSize);
                    } else {
                        canvas.width = imageBitmap.width;
                        canvas.height = imageBitmap.height;
                        const ctx = canvas.getContext('2d');
                        ctx.drawImage(imageBitmap, 0, 0);
                    }
                    
                    window.croppedTextures[key] = canvas.toDataURL('image/png');
                    imageBitmap.close();
                } catch (e) {
                    console.error(`Failed to load texture: ${key}`, e.message);
                }
            }
        }, textureData);
        
        const result = await page.evaluate(async (modelData) => {
            try {
                // Validate model has elements
                if (!modelData.elements || !Array.isArray(modelData.elements) || modelData.elements.length === 0) {
                    return {error: 'Model has no elements array'};
                }
                
                if (window.currentMesh) {
                    window.scene.remove(window.currentMesh);
                    window.currentMesh.geometry.dispose();
                    if (Array.isArray(window.currentMesh.material)) {
                        window.currentMesh.material.forEach(m => m.dispose());
                    } else {
                        window.currentMesh.material.dispose();
                    }
                }
                
                const geometry = new window.MinecraftModelGeometry(modelData);
                const materials = [];
                const loader = new window.THREE.TextureLoader();
                
                // Group 0 is always the fallback material
                materials.push(new window.THREE.MeshBasicMaterial({color: 0xff00ff, side: window.THREE.DoubleSide}));
                
                // Build texture variable to data mapping
                const textureVarToData = {};
                for (const [key, value] of Object.entries(modelData.textures || {})) {
                    if (window.croppedTextures[key]) {
                        textureVarToData[key] = window.croppedTextures[key];
                    }
                }
                
                // Replicate build.js logic: check for duplicate paths (BBModel case)
                const textures = modelData.textures || {};
                const uniquePaths = new Set(Object.values(textures));
                const hasDuplicatePaths = uniquePaths.size < Object.keys(textures).length;
                
                // Create materials in the same order as build.js groups
                if (hasDuplicatePaths) {
                    // BBModel case: group by texture variable (ID) instead of path
                    const groupKeys = Object.keys(textures);
                    const allNumeric = groupKeys.every(k => /^\d+$/.test(k));
                    const sortedKeys = allNumeric ? 
                        groupKeys.sort((a, b) => parseInt(a) - parseInt(b)) :
                        groupKeys.sort();
                    
                    for (const variable of sortedKeys) {
                        const textureData = textureVarToData[variable];
                        if (textureData) {
                            const texture = loader.load(textureData);
                            texture.magFilter = window.THREE.NearestFilter;
                            texture.minFilter = window.THREE.NearestFilter;
                            texture.colorSpace = window.THREE.SRGBColorSpace;
                            texture.generateMipmaps = false;
                            materials.push(new window.THREE.MeshBasicMaterial({
                                map: texture, side: window.THREE.DoubleSide, transparent: true, alphaTest: 0.1
                            }));
                        } else {
                            materials.push(new window.THREE.MeshBasicMaterial({color: 0xff0000, side: window.THREE.DoubleSide}));
                        }
                    }
                } else {
                    // Normal case: group by unique texture paths
                    const sortedPaths = [...uniquePaths].sort();
                    
                    for (const texturePath of sortedPaths) {
                        const variable = Object.keys(textures).find(k => textures[k] === texturePath);
                        const textureData = variable ? textureVarToData[variable] : null;
                        if (textureData) {
                            const texture = loader.load(textureData);
                            texture.magFilter = window.THREE.NearestFilter;
                            texture.minFilter = window.THREE.NearestFilter;
                            texture.colorSpace = window.THREE.SRGBColorSpace;
                            texture.generateMipmaps = false;
                            materials.push(new window.THREE.MeshBasicMaterial({
                                map: texture, side: window.THREE.DoubleSide, transparent: true, alphaTest: 0.1
                            }));
                        } else {
                            materials.push(new window.THREE.MeshBasicMaterial({color: 0xff0000, side: window.THREE.DoubleSide}));
                        }
                    }
                }
                
                const mesh = new window.THREE.Mesh(geometry, materials);
                window.scene.add(mesh);
                window.currentMesh = mesh;
                
                await new Promise(resolve => setTimeout(resolve, 100));
                
                // Step 1: Apply display.gui transformations (rotation only, ignore scale/translation)
                if (modelData.display && modelData.display.gui && modelData.display.gui.rotation) {
                    const [rotX, rotY, rotZ] = modelData.display.gui.rotation;
                    mesh.rotation.order = 'XYZ';
                    mesh.rotation.x = rotX * Math.PI / 180;
                    mesh.rotation.y = rotY * Math.PI / 180;
                    mesh.rotation.z = rotZ * Math.PI / 180;
                }
                
                mesh.updateMatrixWorld(true);
                
                // Step 2: Center the model to (0,0,0)
                const box = new window.THREE.Box3().setFromObject(mesh);
                const center = box.getCenter(new window.THREE.Vector3());
                mesh.position.x -= center.x;
                mesh.position.y -= center.y;
                mesh.position.z -= center.z;
                mesh.updateMatrixWorld(true);
                
                // Step 3: Smart zoom-to-fit with automatic centering
                const canvasSize = 128;
                const targetPadding = 0.1; // Target padding in pixels
                const maxIterations = 40; // More iterations for precision
                
                // Initial frustum estimate - start closer
                const initialBox = new window.THREE.Box3().setFromObject(mesh);
                const initialSize = initialBox.getSize(new window.THREE.Vector3());
                let frustumSize = Math.max(initialSize.x, initialSize.y) * 1.02; // Start much closer
                
                // Camera offset for centering (Y axis adjustment)
                let cameraOffsetY = 0;
                let cameraOffsetX = 0;
                
                for (let iter = 0; iter < maxIterations; iter++) {
                    // Set camera frustum
                    window.camera.left = -frustumSize / 2;
                    window.camera.right = frustumSize / 2;
                    window.camera.top = frustumSize / 2;
                    window.camera.bottom = -frustumSize / 2;
                    window.camera.updateProjectionMatrix();
                    
                    // Apply camera offset for centering
                    window.camera.position.set(cameraOffsetX, cameraOffsetY, 30);
                    window.camera.lookAt(cameraOffsetX, cameraOffsetY, 0);
                    
                    // Render
                    window.renderer.render(window.scene, window.camera);
                    
                    // Read pixels to find content bounds
                    const gl = window.renderer.getContext();
                    const pixels = new Uint8Array(canvasSize * canvasSize * 4);
                    gl.readPixels(0, 0, canvasSize, canvasSize, gl.RGBA, gl.UNSIGNED_BYTE, pixels);
                    
                    let minX = canvasSize, minY = canvasSize;
                    let maxX = 0, maxY = 0;
                    let hasContent = false;
                    
                    for (let y = 0; y < canvasSize; y++) {
                        for (let x = 0; x < canvasSize; x++) {
                            const i = (y * canvasSize + x) * 4;
                            if (pixels[i + 3] > 0) {
                                hasContent = true;
                                if (x < minX) minX = x;
                                if (x > maxX) maxX = x;
                                if (y < minY) minY = y;
                                if (y > maxY) maxY = y;
                            }
                        }
                    }
                    
                    if (!hasContent) {
                        // No content, zoom out
                        frustumSize *= 1.5;
                        continue;
                    }
                    
                    // Calculate padding on each side
                    const padLeft = minX;
                    const padRight = (canvasSize - 1) - maxX;
                    const padTop = minY;
                    const padBottom = (canvasSize - 1) - maxY;
                    
                    // Check if cut off (very strict)
                    if (padLeft < 0.1 || padRight < 0.1 || padTop < 0.1 || padBottom < 0.1) {
                        // Content cut off, zoom out slightly
                        frustumSize *= 1.03;
                        continue;
                    }
                    
                    // Calculate padding imbalance
                    const verticalImbalance = padTop - padBottom;
                    const horizontalImbalance = padLeft - padRight;
                    
                    // Adjust camera position to balance padding
                    if (Math.abs(verticalImbalance) > 0.3) {
                        const adjustment = verticalImbalance * frustumSize / canvasSize * 0.5;
                        cameraOffsetY += adjustment;
                    }
                    
                    if (Math.abs(horizontalImbalance) > 0.3) {
                        const adjustment = horizontalImbalance * frustumSize / canvasSize * 0.5;
                        cameraOffsetX += adjustment;
                    }
                    
                    // Calculate minimum padding
                    const minPadding = Math.min(padLeft, padRight, padTop, padBottom);
                    
                    // Very strict acceptance - only stop when really close to target
                    if (minPadding >= targetPadding && minPadding <= targetPadding * 1.5 &&
                        Math.abs(verticalImbalance) <= 1.0 && Math.abs(horizontalImbalance) <= 1.0) {
                        // Perfect, stop
                        break;
                    }
                    
                    // Aggressive zoom adjustment
                    if (minPadding < targetPadding) {
                        // Too little padding, zoom out
                        frustumSize *= 1.02;
                    } else if (minPadding > targetPadding * 1.5) {
                        // Too much padding, zoom in aggressively
                        frustumSize *= 0.97;
                    }
                }
                
                // Final render with optimized settings
                window.camera.left = -frustumSize / 2;
                window.camera.right = frustumSize / 2;
                window.camera.top = frustumSize / 2;
                window.camera.bottom = -frustumSize / 2;
                window.camera.updateProjectionMatrix();
                window.camera.position.set(cameraOffsetX, cameraOffsetY, 30);
                window.camera.lookAt(cameraOffsetX, cameraOffsetY, 0);
                window.renderer.render(window.scene, window.camera);
                
                const dataUrl = window.renderer.domElement.toDataURL('image/png');
                
                return {success: true, dataUrl};
            } catch (err) {
                return {error: err.message};
            }
        }, modelData);
        
        if (result.error) {
            return false;
        }
        
        const base64Data = result.dataUrl.replace(/^data:image\/png;base64,/, '');
        let imageBuffer = Buffer.from(base64Data, 'base64');
        
        // Remove isolated pixels (noise cleanup) - remove clusters smaller than 3 pixels
        imageBuffer = await removeIsolatedPixels(imageBuffer, 3);
        
        // Save as RGBA 32-bit PNG (no palette, no resize)
        await sharp(imageBuffer)
            .png({ 
                compressionLevel: 9
            })
            .toFile(outputPath);
        
        return true;
    } catch (error) {
        return false;
    }
}

async function generateBlockIcons(page) {
    // Tìm thư mục blockstates
    const possibleBlockstatesDirs = [
        path.join(__dirname, '../pack/assets/minecraft/blockstates'),
        path.join(__dirname, '../../pack/assets/minecraft/blockstates')
    ];
    
    let blockstatesDir = null;
    for (const testPath of possibleBlockstatesDirs) {
        if (fs.existsSync(testPath)) {
            blockstatesDir = testPath;
            break;
        }
    }
    
    if (!blockstatesDir) {
        return;
    }
    
    // Tìm bedrock root
    const possibleBedrockPaths = [
        path.join(__dirname, '../staging/target/rp'),
        path.join(__dirname, '../../staging/target/rp')
    ];
    
    let bedrockRoot = null;
    for (const testPath of possibleBedrockPaths) {
        if (fs.existsSync(testPath)) {
            bedrockRoot = testPath;
            break;
        }
    }
    
    if (!bedrockRoot) {
        return;
    }
    
    // Quét tất cả blockstate files
    const blockstateFiles = fs.readdirSync(blockstatesDir)
        .filter(file => file.endsWith('.json'));
    
    if (blockstateFiles.length === 0) {
        return;
    }
    
    // Thu thập tất cả models từ các blockstate files
    const models = [];
    
    for (const blockstateFile of blockstateFiles) {
        const blockstatePath = path.join(blockstatesDir, blockstateFile);
        const blockName = blockstateFile.replace('.json', '');
        
        try {
            const blockstateData = JSON.parse(fs.readFileSync(blockstatePath, 'utf-8'));
            
            if (blockstateData.variants) {
                for (const [variant, data] of Object.entries(blockstateData.variants)) {
                    if (data.model && !data.model.startsWith('block/') && !data.model.startsWith('minecraft:')) {
                        models.push({ 
                            blockName,
                            variant, 
                            modelPath: data.model 
                        });
                    }
                }
            }
        } catch (error) {
            // Skip on error
        }
    }
    
    if (models.length === 0) {
        return;
    }
    
    let success = 0, skipped = 0;
    
    for (const { blockName, variant, modelPath } of models) {
        // Parse namespace:path
        let namespace = 'minecraft';
        let relativePath = modelPath;
        if (modelPath.includes(':')) {
            [namespace, relativePath] = modelPath.split(':');
        }
        
        // Find attachable
        const attachablePath = path.join(bedrockRoot, 'attachables', namespace, relativePath + '.json');
        
        if (!fs.existsSync(attachablePath)) {
            skipped++;
            continue;
        }
        
        // Read attachable
        const attachableData = JSON.parse(fs.readFileSync(attachablePath, 'utf-8'));
        const description = attachableData['minecraft:attachable']?.description;
        
        if (!description) {
            skipped++;
            continue;
        }
        
        const geometry = description.geometry?.default;
        
        // CHỈ XỬ LÝ geometry.campfire_block
        if (geometry !== 'geometry.campfire_block') {
            skipped++;
            continue;
        }
        
        const textureDefault = description.textures?.default;
        if (!textureDefault) {
            skipped++;
            continue;
        }
        
        // Find texture
        const cleanPath = textureDefault.replace(/^textures\//, '');
        const texturePath = path.join(bedrockRoot, 'textures', cleanPath + '.png');
        
        if (!fs.existsSync(texturePath)) {
            skipped++;
            continue;
        }
        
        // Create block model JSON
        const blockModel = {
            credit: "Made with Blockbench",
            elements: [{
                name: "blocks",
                from: [0, 0, 0],
                to: [16, 16, 16],
                rotation: { angle: 0, axis: "y", origin: [8, 0, 8] },
                color: 3,
                faces: {
                    north: { uv: [0, 0, 16, 16], texture: "#0" },
                    east: { uv: [0, 0, 16, 16], texture: "#0" },
                    south: { uv: [0, 0, 16, 16], texture: "#0" },
                    west: { uv: [0, 0, 16, 16], texture: "#0" },
                    up: { uv: [0, 0, 16, 16], texture: "#0" },
                    down: { uv: [0, 0, 16, 16], texture: "#0" }
                }
            }],
            textures: {
                "0": "block_texture"
            },
            display: {
                gui: {
                    rotation: [30, -135, 0],
                    scale: [0.625, 0.625, 0.625]
                }
            }
        };
        
        // Create output path based on attachable path
        // bedrock/attachables/vanilla_expansion_wool/item/ia_auto/orange_quilt.json
        // -> textures/vanilla_expansion_wool/item/ia_auto/orange_quilt.png
        const relativeAttachablePath = path.relative(path.join(bedrockRoot, 'attachables'), attachablePath);
        const outputName = relativeAttachablePath.replace('.json', '.png');
        const outputPath = path.join(CONFIG.outputDir, 'textures', outputName);
        
        // Create directory if needed
        const outputDir = path.dirname(outputPath);
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }
        
        try {
            // Use the existing generateIcon function with our block model
            const result = await generateBlockIcon(page, blockModel, texturePath, outputPath);
            if (result) {
                success++;
            } else {
                skipped++;
            }
        } catch (error) {
            skipped++;
        }
    }
}

async function generateBlockIcon(page, modelData, texturePath, outputPath) {
    try {
        // Load texture as base64
        const buffer = fs.readFileSync(texturePath);
        const base64 = buffer.toString('base64');
        const textureData = {
            "0": `data:image/png;base64,${base64}`
        };
        
        // Load texture in browser
        await page.evaluate(async (textureData) => {
            window.croppedTextures = {};
            
            for (const [key, dataUrl] of Object.entries(textureData)) {
                try {
                    const response = await fetch(dataUrl);
                    const blob = await response.blob();
                    const imageBitmap = await createImageBitmap(blob);
                    
                    let canvas = document.createElement('canvas');
                    canvas.width = imageBitmap.width;
                    canvas.height = imageBitmap.height;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(imageBitmap, 0, 0);
                    
                    window.croppedTextures[key] = canvas.toDataURL('image/png');
                    imageBitmap.close();
                } catch (e) {
                    console.error(`Failed to load texture: ${key}`, e.message);
                }
            }
        }, textureData);
        
        const result = await page.evaluate(async (modelData) => {
            try {
                if (window.currentMesh) {
                    window.scene.remove(window.currentMesh);
                    window.currentMesh.geometry.dispose();
                    if (Array.isArray(window.currentMesh.material)) {
                        window.currentMesh.material.forEach(m => m.dispose());
                    } else {
                        window.currentMesh.material.dispose();
                    }
                }
                
                const geometry = new window.MinecraftModelGeometry(modelData);
                const loader = new window.THREE.TextureLoader();
                
                const textureData = window.croppedTextures["0"];
                const texture = loader.load(textureData);
                texture.magFilter = window.THREE.NearestFilter;
                texture.minFilter = window.THREE.NearestFilter;
                texture.colorSpace = window.THREE.SRGBColorSpace;
                texture.generateMipmaps = false;
                
                const material = new window.THREE.MeshBasicMaterial({
                    map: texture, 
                    side: window.THREE.DoubleSide, 
                    transparent: true, 
                    alphaTest: 0.1
                });
                
                const mesh = new window.THREE.Mesh(geometry, material);
                window.scene.add(mesh);
                window.currentMesh = mesh;
                
                await new Promise(resolve => setTimeout(resolve, 100));
                
                // Step 1: Apply display.gui scale if present
                let guiScale = 1.0;
                if (modelData.display && modelData.display.gui && modelData.display.gui.scale) {
                    const scaleArray = modelData.display.gui.scale;
                    guiScale = scaleArray[0]; // Use X scale (assuming uniform)
                    mesh.scale.set(guiScale, guiScale, guiScale);
                }
                
                // Step 2: Apply display.gui rotation if present
                if (modelData.display && modelData.display.gui && modelData.display.gui.rotation) {
                    const [rotX, rotY, rotZ] = modelData.display.gui.rotation;
                    mesh.rotation.order = 'XYZ';
                    mesh.rotation.x = rotX * Math.PI / 180;
                    mesh.rotation.y = rotY * Math.PI / 180;
                    mesh.rotation.z = rotZ * Math.PI / 180;
                }
                
                // Step 3: Apply display.gui translation if present
                if (modelData.display && modelData.display.gui && modelData.display.gui.translation) {
                    const [tx, ty, tz] = modelData.display.gui.translation;
                    mesh.position.set(tx, ty, tz);
                }
                
                mesh.updateMatrixWorld(true);
                
                // Step 4: ALWAYS recenter the model to (0,0,0)
                const box = new window.THREE.Box3().setFromObject(mesh);
                const center = box.getCenter(new window.THREE.Vector3());
                mesh.position.x -= center.x;
                mesh.position.y -= center.y;
                mesh.position.z -= center.z;
                mesh.updateMatrixWorld(true);
                
                // Step 5: Calculate bounding box after all transformations
                const finalBox = new window.THREE.Box3().setFromObject(mesh);
                const size = finalBox.getSize(new window.THREE.Vector3());
                
                // Step 6: Scale model to fill 64x64 canvas (block icons use smaller size)
                // Use the larger dimension to ensure model fits
                const maxDimension = Math.max(size.x, size.y);
                const targetCanvasSize = 64;
                const padding = 0.5; // Minimal padding in pixels
                const availableSpace = targetCanvasSize - (padding * 2);
                
                // Calculate frustum size to make model fill the canvas
                const frustumSize = maxDimension * (targetCanvasSize / availableSpace);
                
                // Step 7: Set camera with calculated frustum
                window.camera.left = -frustumSize / 2;
                window.camera.right = frustumSize / 2;
                window.camera.top = frustumSize / 2;
                window.camera.bottom = -frustumSize / 2;
                window.camera.updateProjectionMatrix();
                
                window.camera.position.set(0, 0, 30);
                window.camera.lookAt(0, 0, 0);
                
                // Step 8: Render
                window.renderer.render(window.scene, window.camera);
                const dataUrl = window.renderer.domElement.toDataURL('image/png');
                
                return { success: true, dataUrl };
            } catch (err) {
                return { error: err.message };
            }
        }, modelData);
        
        if (result.error) {
            return false;
        }
        
        const base64Data = result.dataUrl.replace(/^data:image\/png;base64,/, '');
        const imageBuffer = Buffer.from(base64Data, 'base64');
        
        // Convert to 8-bit PNG with alpha (block icons at 64x64)
        await sharp(imageBuffer)
            .png({ 
                compressionLevel: 9,
                palette: true,
                quality: 100,
                colors: 256
            })
            .toFile(outputPath);
        
        return true;
    } catch (error) {
        return false;
    }
}

async function main() {
    // Download and extract assets from Dropbox
    await downloadAndExtractAssets();
    
    const possiblePaths = [CONFIG.assetsDir, './pack/assets', path.join(__dirname, '../pack/assets')];
    let assetsPath = null;
    for (const testPath of possiblePaths) {
        const resolved = path.resolve(testPath);
        if (fs.existsSync(resolved)) {
            assetsPath = resolved;
            break;
        }
    }
    
    if (!assetsPath) {
        process.exit(1);
    }
    
    CONFIG.assetsDir = assetsPath;
    if (!fs.existsSync(CONFIG.outputDir)) fs.mkdirSync(CONFIG.outputDir, {recursive: true});
    
    const modelFiles = findModelFiles(CONFIG.assetsDir);
    
    const html = createHTML();
    const server = await createServer(html);
    
    try {
        const browser = await puppeteer.launch({
            headless: 'shell',
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox', 
                '--disable-web-security',
                '--disable-features=IsolateOrigins',
                '--disable-site-isolation-trials',
                '--allow-file-access-from-files',
                '--disable-blink-features=AutomationControlled'
            ]
        });
        
        // Create parallel workers (pages)
        const WORKERS = process.env.CI ? 2 : 8; // Use 2 workers on CI (GitHub Actions), 8 locally
        
        const workers = [];
        for (let i = 0; i < WORKERS; i++) {
            const page = await browser.newPage();
            await page.setViewport({width: 128, height: 128});
            await page.goto(`http://localhost:${CONFIG.serverPort}`, {waitUntil: 'networkidle0', timeout: 30000});
            await page.waitForFunction(() => window.ready === true, {timeout: 10000});
            workers.push(page);
        }
        
        // Process models in parallel batches
        let success = 0, fail = 0;
        
        for (let i = 0; i < modelFiles.length; i += WORKERS) {
            const batch = [];
            for (let j = 0; j < WORKERS && (i + j) < modelFiles.length; j++) {
                const modelPath = modelFiles[i + j];
                
                const relativePath = path.relative(CONFIG.assetsDir, modelPath);
                const parts = relativePath.split(path.sep);
                
                const modelsIndex = parts.indexOf('models');
                if (modelsIndex >= 0) {
                    parts.splice(modelsIndex, 1);
                }
                
                const outputName = parts.join(path.sep).replace('.json', '.png');
                const outputPath = path.join(CONFIG.outputDir, 'textures', outputName);
                
                const outputDir = path.dirname(outputPath);
                if (!fs.existsSync(outputDir)) {
                    fs.mkdirSync(outputDir, { recursive: true });
                }
                
                batch.push({
                    worker: workers[j],
                    modelPath,
                    outputPath
                });
            }
            
            // Render all models in batch simultaneously
            const batchPromises = batch.map(item => 
                generateIcon(item.worker, item.modelPath, item.outputPath)
            );
            
            const results = await Promise.all(batchPromises);
            
            // Count results
            for (const result of results) {
                if (result) success++;
                else fail++;
            }
        }
        
        // Create a dedicated 64x64 page for block icons
        const blockPage = await browser.newPage();
        await blockPage.setViewport({width: 64, height: 64});
        await blockPage.goto(`http://localhost:${CONFIG.serverPort}`, {waitUntil: 'networkidle0', timeout: 30000});
        await blockPage.waitForFunction(() => window.ready === true, {timeout: 10000});
        
        // Resize canvas and renderer to 64x64 for block icons
        await blockPage.evaluate(() => {
            const canvas = document.getElementById('canvas');
            canvas.width = 64;
            canvas.height = 64;
            window.renderer.setSize(64, 64);
        });
        
        // Generate block icons using dedicated 64x64 page
        await generateBlockIcons(blockPage);
        
        await browser.close();
        
    } finally {
        server.close();
    }
}

main().catch(console.error);
