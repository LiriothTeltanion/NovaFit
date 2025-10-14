#!/usr/bin/env python3
"""Quick test script for NovaFit theme improvements"""

import json
from pathlib import Path

# Test different theme configurations
def test_themes():
    config_path = Path("./data/config.json")
    
    # Ensure data directory exists
    config_path.parent.mkdir(exist_ok=True)
    
    # Test configurations
    themes = [
        {"theme": "dark", "step_goal": 10000, "water_goal": 2.0},
        {"theme": "light", "step_goal": 10000, "water_goal": 2.0}
    ]
    
    print("🎨 NovaFit Theme Tester")
    print("=" * 40)
    
    for i, theme_config in enumerate(themes):
        print(f"\n{i+1}. Testing {theme_config['theme']} theme:")
        print(f"   Config: {theme_config}")
        
        # Save config
        with open(config_path, 'w') as f:
            json.dump(theme_config, f, indent=2)
        
        # Print instructions
        theme_name = theme_config['theme'].title()
        print(f"   ✅ {theme_name} theme config saved!")
        print(f"   💡 Run: python novafit.py --gui")
        print(f"   🔄 Toggle theme in Tools tab to see changes")
        
        if i == 0:
            input("\n   Press Enter to test next theme...")

if __name__ == "__main__":
    test_themes()
    print("\n🎉 Theme testing complete!")
    print("💡 The enhanced dark theme includes:")
    print("   • Modern GitHub-inspired color palette")
    print("   • Better contrast and readability")
    print("   • Gradient effects on progress bars") 
    print("   • Enhanced button and input styling")
    print("   • Improved visual hierarchy")
    print("\n🚀 Launch with: python novafit.py --gui")