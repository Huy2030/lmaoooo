import json
import os


def generate_attack_animations(output_dir: str):
    data = {
        "format_version": "1.8.0",
        "animations": {
            "animation.player.first_person.attack_rotation": {
                "loop": True,
                "bones": {
                    "rightarm": {
                        "position": [
                            "math.sin(variable.attack_time * 180.0) * -12.0",
                            "math.sin((1.0 - variable.attack_time) * (1.0 - variable.attack_time) * 200.0) * 8.0 - variable.attack_time * 10.0",
                            "math.sin(variable.attack_time * 150.0) * 3.0"
                        ],
                        "rotation": [
                            "math.sin((1.0 - variable.attack_time) * (1.0 - variable.attack_time) * 250.0) * -50.0",
                            "math.sin((1.0 - variable.attack_time) * (1.0 - variable.attack_time) * 250.0) * 80.0",
                            "math.sin((1.0 - variable.attack_time) * (1.0 - variable.attack_time) * 250.0) * -30.0"
                        ]
                    }
                }
            },
            "animation.player.first_person.vr_attack_rotation": {
                "loop": True,
                "bones": {
                    "rightarm": {
                        "position": [
                            "6.0 * math.sin(variable.attack_time * 130.0)",
                            "(math.sin((1.0 - variable.attack_time) * (1.0 - variable.attack_time) * 190.0) - 0.7) * 9.0 + 5.0",
                            "math.sin(variable.attack_time * 130.0) * 14.0"
                        ],
                        "rotation": [
                            "32.0 * math.sin(variable.attack_time * -170.0 - 45.0) * 1.4",
                            "15.0 * math.sin(variable.attack_time * 160.0)",
                            "28.0 * math.sin(variable.attack_time * 190.0 + 25.0) * 1.3"
                        ]
                    }
                }
            }
        }
    }

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "animation.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    output_dir = os.path.join("staging", "target", "rp", "animations")
    generate_attack_animations(output_dir)
