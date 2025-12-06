from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import os
from dotenv import load_dotenv
from rag import CareerGuideRAG
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Initialize RAG system with PDF path
rag = CareerGuideRAG(pdf_path="career_resources.pdf")


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/submit-profile', methods=['POST'])
def submit_profile():
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data received'
            }), 400
        
        # Build profile data structure
        profile_data = {
            'personal': {
                'name': data.get('name', ''),
                'field_of_study': data.get('field_of_study', '')
            },
            'skills': {
                'technical_skills': data.get('technical_skills', []) if isinstance(data.get('technical_skills'), list) else [s.strip() for s in str(data.get('technical_skills', '')).split(',') if s.strip()],
                'soft_skills': data.get('soft_skills', []) if isinstance(data.get('soft_skills'), list) else [s.strip() for s in str(data.get('soft_skills', '')).split(',') if s.strip()]
            },
            'interests': {
                'subjects_enjoyed': data.get('subjects_enjoyed', []) if isinstance(data.get('subjects_enjoyed'), list) else [s.strip() for s in str(data.get('subjects_enjoyed', '')).split(',') if s.strip()],
                'preferred_industries': data.get('preferred_industries', []) if isinstance(data.get('preferred_industries'), list) else [s.strip() for s in str(data.get('preferred_industries', '')).split(',') if s.strip()]
            }
        }

        # Clear old recommendations to ensure fresh results
        if 'recommended_roles' in session:
            del session['recommended_roles']
        
        # Store in session
        session['profile_data'] = profile_data

        # Get career recommendations
        recommended_roles = rag.get_career_recommendations(profile_data)
        session['recommended_roles'] = recommended_roles
        return jsonify({
            'success': True,
            'roles': recommended_roles,
            'redirect': url_for('dashboard')
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/dashboard')
def dashboard():
    if 'profile_data' not in session:
        return redirect(url_for('home'))

    role_name = request.args.get('role')
    if not role_name:
        # Show list of recommended roles
        if 'recommended_roles' not in session:
            # Regenerate recommendations if not in session
            recommended_roles = rag.get_career_recommendations(session['profile_data'])
            # Store the full roles in session
            session['recommended_roles'] = recommended_roles
        
        # Prepare roles for display - handle both 'role' and 'title' keys
        display_roles = []
        for role in session['recommended_roles']:
            # Handle different possible key names from LLM response
            role_name_key = role.get('role') or role.get('title', 'Unknown Role')
            match_score = role.get('match_score', 0)
            reason = role.get('reason', 'No reason provided')
            
            display_roles.append({
                'role': role_name_key,
                'match_score': match_score,
                'reason': reason
            })
        
        return render_template('dashboard.html', roles=display_roles)

    try:
        # Regenerate recommendations if not in session
        if 'recommended_roles' not in session:
            recommended_roles = rag.get_career_recommendations(session['profile_data'])
            session['recommended_roles'] = recommended_roles

        # Get the original role name from the URL-encoded version and find match_score
        original_role_name = None
        match_score = None
        
        # Normalize the role_name from URL (handle special characters)
        normalized_url_role = role_name.lower().replace('-', ' ').replace('_', ' ')
        
        for role in session['recommended_roles']:
            # Handle both 'role' and 'title' keys
            role_name_in_dict = role.get('role') or role.get('title')
            if role_name_in_dict:
                # Normalize the role name for comparison (handle special characters)
                normalized_role = role_name_in_dict.lower().replace('/', ' ').replace('(', ' ').replace(')', ' ').replace('-', ' ')
                # Remove extra spaces and compare
                normalized_role = ' '.join(normalized_role.split())
                normalized_url_role_clean = ' '.join(normalized_url_role.split())
                
                if normalized_role == normalized_url_role_clean or normalized_role.startswith(normalized_url_role_clean) or normalized_url_role_clean.startswith(normalized_role):
                    original_role_name = role_name_in_dict
                    match_score = role.get('match_score', 0)
                    break

        if not original_role_name:
            flash('Role not found', 'error')
            return redirect(url_for('dashboard'))

        # Get detailed information about the selected role
        role_details = rag.get_role_details(original_role_name, session.get('profile_data'))
        if not role_details or 'error' in role_details:
            flash('Error loading role details', 'error')
            return redirect(url_for('dashboard'))

        # Add match_score to role_details if not already present
        if 'match_score' not in role_details or role_details.get('match_score') is None:
            role_details['match_score'] = match_score if match_score is not None else 0

        return render_template('role_details.html', role=role_details)

    except Exception as e:
        flash('An error occurred while loading role details', 'error')
        return redirect(url_for('dashboard'))


@app.route('/api/role/<role_name>')
def get_role_details(role_name):
    try:
        role_details = rag.get_role_details(role_name, session.get('profile_data'))
        if not role_details or 'error' in role_details:
            return jsonify({
                'success': False,
                'error': 'Role details not found'
            }), 404

        return jsonify({
            'success': True,
            'data': role_details
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True)