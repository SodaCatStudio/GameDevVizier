import os
from flask import Flask, request, jsonify
from openai import OpenAI
from datetime import datetime
import uuid
import json

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("💡 Tip: Install python-dotenv to use .env files: pip install python-dotenv")

app = Flask(__name__)

# Add CORS support
try:
    from flask_cors import CORS
    CORS(app, origins="*")  # Allow all origins for development
    print("✅ CORS enabled for all origins")
except ImportError:
    print("Tip: Install flask-cors for better browser support: pip install flask-cors")

try:
    # Try multiple environment variable names for flexibility
    api_key = (os.environ.get('OPENAI_KEY') or 
               os.environ.get('OPENAI_API_KEY') or 
               os.environ.get('OPENAI_TOKEN'))

    if not api_key:
        raise ValueError("OpenAI API key not found in environment variables")

    client = OpenAI(api_key=api_key)
    print("✅ OpenAI client initialized successfully")

except Exception as e:
    print(f"❌ Failed to initialize OpenAI client: {str(e)}")
    client = None

def analyze_game(business_data):
    """The Game Dev Vizier offers his council."""
    if client is None:
        return "OpenAI client is not initialized. Please check your API key and environment variables."

    prompt = f"""
    You are an expert video game designer and royal vizier. Using the game summary given, share one strong point about it, three ways it could be improved, and three ways the game idea could be made more marketable and have more mass appeal. Be sure to give specific, actionable recommendations and examples especially for how it could be more marketable. Sign off with "Your humble vizier".

    Game Summary:
    {business_data}

    IMPORTANT: Use professional consulting language with perfect spelling and grammar and a royal vizier style as if talking to a king or queen. Format your response with clear sections using markdown headers.
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a top-tier game dev consultant and royal vizier who delivers precise, actionable insights with perfect spelling and grammar."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.85,
        max_tokens=2000
    )

    return response.choices[0].message.content

def process_game_analysis(data):
    """Process game analysis and return results directly"""
    # Validate required fields
    required_fields = ['business_name', 'game_data']
    for field in required_fields:
        if field not in data or data[field] is None:
            raise ValueError(f'Missing required field: {field}')

    business_name = data['business_name']
    game_data = data['game_data']

    # Generate analysis
    print(f"Generating analysis for {business_name}...")
    analysis = analyze_game(game_data)

    # Generate report ID for tracking
    report_id = str(uuid.uuid4())[:8]

    return {
        'success': True,
        'message': 'Game analysis completed successfully!',
        'report_id': report_id,
        'business_name': business_name,
        'analysis': analysis,
        'generated_at': datetime.now().strftime("%B %d, %Y at %I:%M %p")
    }

@app.route('/')
def home():
    """Root endpoint"""
    openai_key = os.environ.get('OPENAI_KEY') or os.environ.get('OPENAI_API_KEY')

    return jsonify({
        'message': 'Game Dev Vizier API is running!',
        'status': 'healthy',
        'endpoints': {
            'health': '/api/health',
            'analyze': '/api/analyze-game (POST)',
            'test': '/api/test (POST)'
        },
        'environment_check': {
            'openai_key_set': bool(openai_key),
            'client_ready': bool(client)
        }
    })

@app.route('/api/analyze-game', methods=['POST'])
def api_analyze_game():
    """Main API endpoint for game analysis"""
    try:
        data = request.json

        # Check if data is None (no JSON in request)
        if data is None:
            return jsonify({'error': 'No JSON data provided'}), 400

        response_data = process_game_analysis(data)
        return jsonify(response_data)

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"❌ Error in API: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Game Dev Vizier',
        'environment': {
            'openai_configured': bool(client)
        }
    })

@app.route('/api/test', methods=['POST'])
def test_endpoint():
    """Test endpoint with sample data"""
    sample_data = {
        'business_name': 'Sample Game Idea',
        'game_data': """
        A visual novel about a detective who solves mysteries about a team of thieves using his unique psychic abilities. The game features a rich storyline, engaging puzzles, and a cast of memorable characters. The game is set in a Victorian-era city and explores themes of mystery, suspense, and the psychic powers that must be used and defeated. The game is designed to be played on PC and mobile devices.
        """
    }

    try:
        print("🧪 Running test with sample data...")
        response_data = process_game_analysis(sample_data)
        return jsonify(response_data)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"❌ Error in test endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/test')
def test_page():
    """Serve the test HTML page"""
    return r'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Game Dev Vizier</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        h1 {
            color: #667eea;
            text-align: center;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #333;
        }
        input, textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
            box-sizing: border-box;
        }
        input:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        textarea {
            height: 150px;
            resize: vertical;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            cursor: pointer;
            width: 100%;
            margin: 10px 0;
            transition: transform 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
        }
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .response {
            margin-top: 20px;
            padding: 20px;
            border-radius: 8px;
        }
        .success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        .loading {
            text-align: center;
            padding: 20px;
            color: #667eea;
        }
        .analysis-result {
            background: #f8f9fa;
            border: 2px solid #667eea;
            border-radius: 10px;
            padding: 25px;
            margin-top: 20px;
        }
        .analysis-result h2 {
            color: #667eea;
            margin-top: 0;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .analysis-content {
            line-height: 1.6;
            font-size: 16px;
            white-space: pre-wrap;
        }
        .analysis-meta {
            background: #e9ecef;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
            color: #6c757d;
        }
        .form-section {
            border-bottom: 2px solid #eee;
            padding-bottom: 30px;
            margin-bottom: 30px;
        }
        .intro-section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 30px;
        }
        .intro-section h3 {
            color: #667eea;
            margin-bottom: 15px;
        }
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            text-align: left;
            margin-top: 20px;
        }
        .feature-item {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 The Game Dev Vizier</h1>

        <div class="intro-section">
            <h3>Get Expert Analysis for Your Game Idea</h3>
            <p style="color: #666; font-size: 18px; margin-bottom: 0;">
                Receive professional insights, improvement suggestions, and marketing strategies instantly
            </p>

            <div class="features-grid">
                <div class="feature-item">
                    <strong>💪 Strengths Analysis</strong><br>
                    <small>What makes your game stand out</small>
                </div>
                <div class="feature-item">
                    <strong>🔧 Improvement Areas</strong><br>
                    <small>Three ways to enhance your game</small>
                </div>
                <div class="feature-item">
                    <strong>💰 Marketability</strong><br>
                    <small>Ways to make your game profitable</small>
                </div>
            </div>
        </div>

        <div class="form-section">
            <div class="form-group">
                <label for="businessName">Game Name:</label>
                <input type="text" id="businessName" placeholder="Enter your game's name" value="">
            </div>

            <div class="form-group">
                <label for="gameData">Game Description:</label>
                <textarea id="gameData" placeholder="Describe your game idea in detail. Include the genre, gameplay mechanics, story, target audience, platform, and any unique features..."></textarea>
            </div>

            <button class="btn" onclick="submitAnalysis()">✨ Get My Game Analysis</button>
            <button class="btn" onclick="alert('JavaScript is working!')" style="background: #28a745; margin-top: 10px;">🧪 Test JavaScript</button>
        </div>

        <div id="response"></div>
    </div>

    <script>
        const apiUrl = window.location.origin;

        function showLoading() {
            document.getElementById('response').innerHTML = '<div class="loading">🔄 Analyzing your game... This may take 30-60 seconds.</div>';
        }

        function showResponse(data, isError = false) {
            const responseDiv = document.getElementById('response');

            if (isError) {
                responseDiv.innerHTML = `<div class="response error">❌ Error: ${data.error || JSON.stringify(data, null, 2)}</div>`;
            } else if (data.success) {
                responseDiv.innerHTML = `
                    <div class="analysis-result">
                        <h2>📊 Your Game Analysis Results</h2>
                        <div class="analysis-meta">
                            <strong>Game:</strong> ${data.business_name}<br>
                            <strong>Report ID:</strong> ${data.report_id}<br>
                            <strong>Generated:</strong> ${data.generated_at}
                        </div>
                        <div class="analysis-content">${formatAnalysis(data.analysis)}</div>
                    </div>
                `;

                // Scroll to results
                responseDiv.scrollIntoView({ behavior: 'smooth' });
            } else {
                responseDiv.innerHTML = `<div class="response error">❌ ${data.error || 'Unknown error occurred'}</div>`;
            }
        }

        function formatAnalysis(analysis) {
            // Simple formatting to make the analysis more readable
            return analysis
                .replace(/## (.*)/g, '<h3 style="color: #667eea; margin-top: 25px; margin-bottom: 10px;">$1</h3>')
                .replace(/### (.*)/g, '<h4 style="color: #764ba2; margin-top: 20px; margin-bottom: 8px;">$1</h4>')
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/\n\n/g, '</p><p>')
                .replace(/^/, '<p>')
                .replace(/$/, '</p>');
        }

        function showInfo(message) {
            document.getElementById('response').innerHTML = `<div class="response info">${message}</div>`;
        }

        async function submitAnalysis() {
            console.log('🔄 submitAnalysis called'); // Debug log

            const businessName = document.getElementById('businessName').value.trim();
            const gameData = document.getElementById('gameData').value.trim();

            console.log('📝 Form data:', { businessName, gameData: gameData.substring(0, 50) + '...' }); // Debug log

            // Validation
            if (!businessName) {
                console.log('❌ Missing business name'); // Debug log
                showInfo('Please enter your game name!');
                return;
            }

            if (!gameData) {
                console.log('❌ Missing game data'); // Debug log
                showInfo('Please describe your game idea!');
                return;
            }

            if (gameData.length < 50) {
                console.log('❌ Game data too short:', gameData.length); // Debug log
                showInfo('Please provide a more detailed description of your game (at least 50 characters).');
                return;
            }

            // Get button reference BEFORE showing loading - FIX FOR BUTTON ISSUE
            const button = document.querySelector('.btn');
            console.log('🔘 Button found:', !!button); // Debug log

            if (button) {
                button.disabled = true;
                button.textContent = '🔄 Analyzing...';
            }

            showLoading();

            console.log('🌐 Making API call to:', `${apiUrl}/api/analyze-game`); // Debug log

            try {
                const response = await fetch(`${apiUrl}/api/analyze-game`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        business_name: businessName,
                        game_data: gameData
                    })
                });

                console.log('📡 Response status:', response.status); // Debug log
                const data = await response.json();
                console.log('📄 Response data:', data); // Debug log

                showResponse(data, !response.ok);
            } catch (error) {
                console.error('❌ Fetch error:', error); // Debug log
                showResponse({ error: error.message }, true);
            } finally {
                // Re-enable button
                if (button) {
                    button.disabled = false;
                    button.textContent = '✨ Get My Game Analysis';
                }
            }
        }
    </script>
</body>
</html>'''

if __name__ == '__main__':
    print("🚀 Starting Game Dev Vizier API...")
    print("📧 Environment Variables Check:")
    print(f"   OPENAI_KEY: {'✅ Set' if os.environ.get('OPENAI_KEY') or os.environ.get('OPENAI_API_KEY') else '❌ Missing'}")

    # Get port from environment variable, default to 5000 for local development
    port = int(os.environ.get('PORT', 5000))

    # Check if we're in production (Railway sets PORT automatically)
    is_production = os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('PORT')

    if is_production:
        print(f"🌐 Production mode detected, running on port {port}")
        print("💡 Note: In production, use 'gunicorn --bind 0.0.0.0:$PORT main:app' instead")
    else:
        print(f"🛠️ Development mode, running on port {port}")

    app.run(debug=False, host='0.0.0.0', port=port)