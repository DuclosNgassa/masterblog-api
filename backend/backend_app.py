from app import create_app

app = create_app()

if __name__ == '__main__':
    # Starts the local development server
    app.run(debug=True, host='0.0.0.0', port=5002)