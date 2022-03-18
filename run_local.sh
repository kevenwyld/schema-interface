APP_DIR=$(pwd)

echo "Creating bundle.js"

cd "$APP_DIR"/static
npm run build
cd "$APP_DIR"

echo "Starting server"

export FLASK_APP=app.py
export FLASK_ENV=development
flask run -p 8081