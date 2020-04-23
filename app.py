from quandromy import create_app
#from quandromy import database

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
