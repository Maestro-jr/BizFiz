from  cloud.shared.security.passwords import create_master_credentials

key_path = "cloudTemplateProject/credentials/master.key"
enc_path = "cloudTemplateProject/credentials/master.enc"

password = create_master_credentials(key_path, enc_path)
print("MASTER PASSWORD:", password)
print("Stored encrypted in credentials folder.")
