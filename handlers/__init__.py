from handlers.onboarding import router as onboarding_router
from handlers.diary      import router as diary_router
from handlers.chat       import router as chat_router
from handlers.sos        import router as sos_router
from handlers.menu       import router as menu_router

all_routers = [
    onboarding_router,
    diary_router,
    chat_router,
    sos_router,
    menu_router,
]
