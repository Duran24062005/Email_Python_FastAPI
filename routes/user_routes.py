from fastapi import APIRouter



user_router = APIRouter()


# public routes
@user_router.get('/{id}', status_code=200)
def get_user_by_id():
    pass

# Administratives routes
@user_router.put('/{id}', status_code=200)
def update_user(data: str):
    pass

@user_router.get('/', status_code=200)
def get_all_user():
    pass

@user_router.get('/admin/pending', status_code=200)
def get_pending_user():
    pass

@user_router.post('/{id}/approve', status_code=200)
def aprove_user():
    pass

@user_router.get('/{id}', status_code=200)
def rejet_user():
    pass

@user_router.patch('/{id}/status', status_code=200)
def change_user_status():
    pass

# estadistics
@user_router.get('/admin/stats', status_code=200)
def get_user_by_id():
    pass