
python -m pip install -r requirements.txt

cd static
npm install
npm run build
cd ..

$env:FLASK_APP = "app.py"
$env:FLASK_ENV = "production"
flask run