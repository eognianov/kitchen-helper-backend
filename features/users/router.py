"""
Router/controller should be responsible only for input data validation and calling the respective operation from operations
You must not work directly with db here

Flow here should be:
    - receive request
    - validate input data
    - call the processing bisness logic function
    - prepare the response
    - return response

"""
import fastapi
from .input_models import CreateUserInputModel
from .operations import create_user, login

router = fastapi.APIRouter()

@router.post('/register')
def register(new_user: CreateUserInputModel):
    result = create_user(new_user)
    # prepare the response
    return result

@router.login('/login')
def login(username: str, password: str):
    result = login(username, password)