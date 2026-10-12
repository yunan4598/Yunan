import bcrypt

# كلمة السر: 459855 (مشفّرة بنجاح)
hashed_password = "$2b$12$eImiTXuWVxfM37uY4JANj.K2r7kG4G0I21RjA5qV4y.VnF2pQJ252"

user_json = f'{{"yunan":{{"pw_hash":"{hashed_password}", "role":"admin"}}}}'

print("انسخ السطر أدناه وضعه داخل Secrets في Streamlit Cloud:")
print(f"APP_USERS = '{user_json}'")
