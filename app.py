from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='static')
CORS(app)  # Allow frontend to communicate with backend

# Database of healthy substitutions
SUBSTITUTIONS = {
    "butter": {
        "replacements": [
            {
                "name": "applesauce",
                "ratio": "1:1 (use 3/4 cup for 1 cup butter)",
                "benefits": "Reduces fat, adds moisture, natural sweetness",
                "best_for": "muffins, quick breads, cakes",
                "taste_score": 8
            },
            {
                "name": "mashed avocado",
                "ratio": "1:1",
                "benefits": "Healthy fats, creamy texture, nutrients",
                "best_for": "brownies, chocolate cakes",
                "taste_score": 7
            },
            {
                "name": "greek yogurt",
                "ratio": "1:2 (1/2 cup yogurt for 1 cup butter)",
                "benefits": "Protein boost, moisture, tangy flavor",
                "best_for": "cakes, muffins, cookies",
                "taste_score": 9
            }
        ]
    },
    "sugar": {
        "replacements": [
            {
                "name": "honey",
                "ratio": "3/4 cup honey for 1 cup sugar (reduce liquid by 1/4 cup)",
                "benefits": "Natural sweetener, antioxidants",
                "best_for": "cookies, cakes, bread",
                "taste_score": 9
            },
            {
                "name": "maple syrup",
                "ratio": "3/4 cup for 1 cup sugar (reduce liquid by 3 tbsp)",
                "benefits": "Minerals, unique flavor",
                "best_for": "pancakes, muffins, oatmeal cookies",
                "taste_score": 8
            },
            {
                "name": "coconut sugar",
                "ratio": "1:1",
                "benefits": "Lower glycemic index, minerals",
                "best_for": "all baked goods",
                "taste_score": 8
            }
        ]
    },
    "all-purpose flour": {
        "replacements": [
            {
                "name": "whole wheat flour",
                "ratio": "1:1 (or mix 50/50 with AP flour)",
                "benefits": "More fiber, nutrients, protein",
                "best_for": "bread, muffins, cookies",
                "taste_score": 7
            },
            {
                "name": "almond flour",
                "ratio": "1:1 (may need binding agent)",
                "benefits": "Gluten-free, protein, healthy fats",
                "best_for": "cookies, cakes, pie crusts",
                "taste_score": 8
            },
            {
                "name": "oat flour",
                "ratio": "1:1.3 (use slightly more oat flour)",
                "benefits": "Gluten-free option, fiber, mild flavor",
                "best_for": "pancakes, muffins, cookies",
                "taste_score": 7
            }
        ]
    },
    "eggs": {
        "replacements": [
            {
                "name": "flax egg",
                "ratio": "1 tbsp ground flax + 3 tbsp water = 1 egg",
                "benefits": "Omega-3, fiber, vegan",
                "best_for": "pancakes, muffins, cookies",
                "taste_score": 7
            },
            {
                "name": "chia egg",
                "ratio": "1 tbsp chia seeds + 3 tbsp water = 1 egg",
                "benefits": "Protein, omega-3, antioxidants",
                "best_for": "brownies, quick breads",
                "taste_score": 7
            },
            {
                "name": "mashed banana",
                "ratio": "1/4 cup mashed banana = 1 egg",
                "benefits": "Potassium, natural sweetness, moisture",
                "best_for": "cakes, muffins, pancakes",
                "taste_score": 8
            }
        ]
    }
}

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/ingredients', methods=['GET'])
def get_ingredients():
    """Get list of all ingredients that can be substituted"""
    return jsonify(list(SUBSTITUTIONS.keys()))

@app.route('/api/substitute/<ingredient>', methods=['GET'])
def get_substitutes(ingredient):
    """Get healthy substitutes for a specific ingredient"""
    ingredient_lower = ingredient.lower()
    
    if ingredient_lower in SUBSTITUTIONS:
        return jsonify({
            "ingredient": ingredient,
            "substitutions": SUBSTITUTIONS[ingredient_lower]["replacements"]
        })
    else:
        return jsonify({
            "error": "Ingredient not found",
            "available_ingredients": list(SUBSTITUTIONS.keys())
        }), 404

@app.route('/api/substitute', methods=['POST'])
def suggest_substitution():
    """
    Suggest best substitution based on recipe type and preferences
    Expects JSON: {"ingredient": "butter", "recipe_type": "cookies", "priority": "taste"}
    """
    data = request.json
    ingredient = data.get('ingredient', '').lower()
    recipe_type = data.get('recipe_type', '').lower()
    priority = data.get('priority', 'balanced')  # taste, health, or balanced
    
    if ingredient not in SUBSTITUTIONS:
        return jsonify({"error": "Ingredient not found"}), 404
    
    replacements = SUBSTITUTIONS[ingredient]["replacements"]
    
    # Filter by recipe type if specified
    if recipe_type:
        filtered = [r for r in replacements if recipe_type in r['best_for'].lower()]
        if filtered:
            replacements = filtered
    
    # Sort by priority
    if priority == 'taste':
        replacements = sorted(replacements, key=lambda x: x['taste_score'], reverse=True)
    
    return jsonify({
        "ingredient": ingredient,
        "recommended": replacements[0] if replacements else None,
        "alternatives": replacements[1:] if len(replacements) > 1 else []
    })

@app.route('/api/analyze-recipe', methods=['POST'])
def analyze_recipe():
    """
    Analyze a full recipe and suggest substitutions
    Expects JSON: {"ingredients": ["1 cup butter", "2 cups sugar", "3 eggs"]}
    """
    data = request.json
    ingredients_list = data.get('ingredients', [])
    
    suggestions = []
    
    for ingredient_line in ingredients_list:
        # Simple parsing - look for keywords
        ingredient_line_lower = ingredient_line.lower()
        
        for key_ingredient in SUBSTITUTIONS.keys():
            if key_ingredient in ingredient_line_lower:
                best_sub = SUBSTITUTIONS[key_ingredient]["replacements"][0]
                suggestions.append({
                    "original": ingredient_line,
                    "ingredient": key_ingredient,
                    "suggested_replacement": best_sub
                })
                break
    
    return jsonify({
        "total_ingredients": len(ingredients_list),
        "substitutions_found": len(suggestions),
        "suggestions": suggestions
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)