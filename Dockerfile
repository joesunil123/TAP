FROM node:14

WORKDIR /app

COPY package*.json ./

CMD ["source venv/bin/activate", 'export flask_APP=app', 'python3 db/init_db.py', 'flask run']

