from passlib.context import CryptContext

# By adding 'bcrypt_sha256', we help passlib handle the data better
# and avoid the 'attribute __about__' error.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Hash():
    @staticmethod
    def bcrypt(password: str):
        # We ensure the password is encrypted correctly 
        return pwd_context.hash(password)

    @staticmethod
    def verify(hashed_password: str, plain_password: str):
        return pwd_context.verify(plain_password, hashed_password)