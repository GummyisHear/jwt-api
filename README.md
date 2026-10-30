# JWT mini-API

Flask + PyJWT näide: /login, /profiil, /admin.

## Käivitamine
```bash
pip install flask pyjwt
pip install python-dotnet
python app.py
```

## Testkasutajad
- mari / maasikas1 (student)
- juhan / admin123 (admin)

## Lõpp-punktid
- POST /login: body `{"kasutajanimi": "...", "parool": "..."}`, tagastab tokeni
- GET /profiil: vajab `Authorization: Bearer <token>`
- GET /admin: vajab admin-rolliga tokenit