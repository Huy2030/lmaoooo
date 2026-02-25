import {
    BufferGeometry, Matrix3, Vector3,
    Float32BufferAttribute, Uint16BufferAttribute
} from 'three';

const vertexMaps = {
    west: [0, 1, 2, 3],
    east: [4, 5, 6, 7],
    down: [0, 3, 4, 7],
    up: [2, 1, 6, 5],
    north: [7, 6, 1, 0],
    south: [3, 2, 5, 4]
};

function applyVertexMapRotation(rotation, vertices) {
    const [a, b, c, d] = vertices;
    return (
        rotation === 0 ? [a, b, c, d] :
            rotation === 90 ? [b, c, d, a] :
                rotation === 180 ? [c, d, a, b] :
                    [d, a, b, c]
    );
}

function buildMatrix(angle, scale, axis) {
    const a = Math.cos(angle) * scale;
    const b = Math.sin(angle) * scale;
    const matrix = new Matrix3();

    if (axis === 'x') {
        matrix.set(
            1, 0, 0,
            0, a, -b,
            0, b, a
        );
    } else if (axis === 'y') {
        matrix.set(
            a, 0, b,
            0, 1, 0,
            -b, 0, a
        );
    } else {
        matrix.set(
            a, -b, 0,
            b, a, 0,
            0, 0, 1
        );
    }

    return matrix;
}

function rotateCubeCorners(corners, rotation) {
    // Validate rotation object has required properties
    if (!rotation || !rotation.origin || !Array.isArray(rotation.origin)) {
        console.warn('Invalid rotation data, skipping rotation:', rotation);
        return corners;
    }
    
    const origin = new Vector3()
        .fromArray(rotation.origin)
        .subScalar(8);

    const angle = rotation.angle / 180 * Math.PI;
    const scale = rotation.rescale ? Math.SQRT2 / Math.sqrt(Math.cos(angle || Math.PI / 4) ** 2 * 2) : 1;
    const matrix = buildMatrix(angle, scale, rotation.axis);

    return corners.map(vertex => new Vector3()
        .fromArray(vertex)
        .sub(origin)
        .applyMatrix3(matrix)
        .add(origin)
        .toArray()
    );
}

function getCornerVertices(from, to) {
    const [x1, y1, z1, x2, y2, z2] = from.concat(to).map(coordinate => coordinate - 8);

    return [
        [x1, y1, z1],
        [x1, y2, z1],
        [x1, y2, z2],
        [x1, y1, z2],
        [x2, y1, z2],
        [x2, y2, z2],
        [x2, y2, z1],
        [x2, y1, z1]
    ];
}

function generateDefaultUvs(faceName, from, to) {
    const [x1, y1, z1] = from;
    const [x2, y2, z2] = to;

    return (
        faceName === 'west' ? [z1, 16 - y2, z2, 16 - y1] :
            faceName === 'east' ? [16 - z2, 16 - y2, 16 - z1, 16 - y1] :
                faceName === 'down' ? [x1, 16 - z2, x2, 16 - z1] :
                    faceName === 'up' ? [x1, z1, x2, z2] :
                        faceName === 'north' ? [16 - x2, 16 - y2, 16 - x1, 16 - y1] :
                            [x1, 16 - y2, x2, 16 - y1]
    );
}

function computeNormalizedUvs(uvs, resolution = { width: 16, height: 16 }) {
    const width = resolution.width || 16;
    const height = resolution.height || 16;
    
    // Small inset to prevent texture bleeding at edges
    const insetU = 0.0001;  // Reduced inset in normalized UV space
    const insetV = 0.0001;
    
    // uvs array is [u1, v1, u2, v2] representing the UV rectangle
    const [u1, v1, u2, v2] = uvs;
    
    // Normalize coordinates
    let nu1 = u1 / width;
    let nv1 = (height - v1) / height;
    let nu2 = u2 / width;
    let nv2 = (height - v2) / height;
    
    // Apply inset: shrink the UV rect slightly inward
    // Determine which is min/max for each axis and apply inset accordingly
    if (nu1 < nu2) {
        nu1 += insetU;
        nu2 -= insetU;
    } else {
        nu1 -= insetU;
        nu2 += insetU;
    }
    
    if (nv1 < nv2) {
        nv1 += insetV;
        nv2 -= insetV;
    } else {
        nv1 -= insetV;
        nv2 += insetV;
    }
    
    return [nu1, nv1, nu2, nv2];
}

class GroupedAttributesBuilder {
    constructor(textures) {
        this.groups = {};
        this.groupMapping = {};
        this.missingGroup = { vertices: [], uvs: [], indices: [], tintEnabled: false };

        // Check if all textures have the same path (BBModel case)
        const uniquePaths = new Set(Object.values(textures));
        const hasDuplicatePaths = uniquePaths.size < Object.keys(textures).length;

        if (hasDuplicatePaths) {
            // BBModel case: group by texture variable (ID) instead of path
            for (const variable in textures) {
                this.groups[variable] = { vertices: [], uvs: [], indices: [], tintEnabled: false };
                this.groupMapping['#' + variable] = this.groups[variable];
            }
        } else {
            // Normal case: group by texture path
            for (const texturePath of uniquePaths) {
                this.groups[texturePath] = { vertices: [], uvs: [], indices: [], tintEnabled: false };
            }
            for (const variable in textures) {
                this.groupMapping['#' + variable] = this.groups[textures[variable]];
            }
        }
    }

    getContext(textureVariable, tintIndex) {
        const group = this.groupMapping[textureVariable] || this.missingGroup;
        group.tintEnabled = tintIndex !== undefined ? tintIndex !== -1 : false;
        return group;
    }

    getAttributes() {
        let { vertices, uvs, indices } = this.missingGroup;
        let indexCount = indices.length;

        const groups = [{ start: 0, count: indexCount, materialIndex: 0, tintEnabled: false }];

        // Sort keys numerically if they're all numbers (BBModel case), otherwise sort as strings
        const groupKeys = Object.keys(this.groups);
        const allNumeric = groupKeys.every(key => /^\d+$/.test(key));
        const sortedKeys = allNumeric ? 
            groupKeys.sort((a, b) => parseInt(a) - parseInt(b)) : 
            groupKeys.sort();

        groups.push(...sortedKeys.map((key, i) => {
            const group = this.groups[key];
            const start = indexCount;
            const count = group.indices.length;
            const offset = vertices.length / 3;

            vertices = vertices.concat(group.vertices);
            uvs = uvs.concat(group.uvs);
            indices = indices.concat(group.indices.map(index => index + offset));

            indexCount += count;

            return { start, count, materialIndex: i + 1, tintEnabled: group.tintEnabled };
        }));

        return { vertices, uvs, indices, groups };
    }
}

function sanitizeTextureReferences(model) {
    for (const element of model.elements) {
        for (const faceName in element.faces) {
            const face = element.faces[faceName];
            
            // Convert numeric texture references to string format
            if (typeof face.texture === 'number') {
                face.texture = `#${face.texture}`;
            } else if (typeof face.texture === 'string') {
                // Fix double-hash references
                if (face.texture.startsWith('##')) {
                    face.texture = face.texture.replace('##', '#');
                }
                // Ensure it starts with # if it's just a number
                else if (face.texture.match(/^\d+$/)) {
                    face.texture = `#${face.texture}`;
                }
            }
        }
    }
    return model;
}

export class MinecraftModelGeometry extends BufferGeometry {
    constructor(model) {
        model = sanitizeTextureReferences(model); // Sanitize model before processing
        super();
        const { vertices, uvs, indices, groups } = MinecraftModelGeometry.computeAttributes(model);

        this.setAttribute('position', new Float32BufferAttribute(vertices, 3));
        this.setAttribute('uv', new Float32BufferAttribute(uvs, 2));
        this.setIndex(new Uint16BufferAttribute(indices, 1));

        for (const { start, count, materialIndex } of groups) {
            this.addGroup(start, count, materialIndex);
        }

        this.tints = groups.map(g => g.tintEnabled);
    }

    faceHasTint(index) {
        return this.tints[index + 1];
    }

    static computeAttributes(model) {
        const builder = new GroupedAttributesBuilder(model.textures);
        const resolution = model.resolution || { width: 16, height: 16 };
        
        for (const element of model.elements) {
            // Skip elements with "hitbox" in their name (case-insensitive)
            if (element.name && element.name.toLowerCase().includes('hitbox')) {
                continue;
            }
            
            const { from, to, rotation } = element;
            
            // Skip elements with invalid geometry data
            if (!from || !to || !Array.isArray(from) || !Array.isArray(to)) {
                console.warn('Skipping element with invalid geometry:', element);
                continue;
            }
            
            const cornerVertices = getCornerVertices(from, to);
            const rotatedVertices = rotation ? rotateCubeCorners(cornerVertices, rotation) : cornerVertices;

            for (const name in element.faces) {
                const faceName = name;
                const face = element.faces[faceName];

                if (face === undefined) {
                    continue;
                }

                const { vertices, uvs, indices } = builder.getContext(face.texture, face.tintindex);

                const i = vertices.length / 3;
                indices.push(i, i + 2, i + 1);
                indices.push(i, i + 3, i + 2);

                for (const index of applyVertexMapRotation(face.rotation || 0, vertexMaps[faceName])) {
                    vertices.push(...rotatedVertices[index]);
                }

                const faceUvs = face.uv || generateDefaultUvs(faceName, from, to);
                const [u1, v1, u2, v2] = computeNormalizedUvs(faceUvs, resolution);
                
                // Debug first element only
                if (vertices.length === 0 && faceName === 'north') {
                    console.log('🔍 First face UVs - Input:', faceUvs, '→ Normalized:', [u1, v1, u2, v2]);
                    console.log('🔍 Resolution used:', resolution);
                }

                uvs.push(u1, v2);
                uvs.push(u1, v1);
                uvs.push(u2, v1);
                uvs.push(u2, v2);
            }
        }

        return builder.getAttributes();
    }
}