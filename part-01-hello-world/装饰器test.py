import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
'''
推荐使用调试逐步骤的单步调试方式来理解装饰器的执行流程。以下是一个简单的示例，展示了如何使用装饰器来注册路由，并模拟处理 HTTP 请求。
'''
class APIRouter:
    def __init__(self):
        self.routes = {}

    def get(self, path):
        def decorator(func):
            # 注册路由
            logging.debug(f"注册路由: {path}")
            self.routes[path] = func
            return func
        return decorator

    def handle_request(self, path):
        logging.debug(f"处理请求路径: {path}")
        # 如果路径存在，调用对应的函数
        if path in self.routes:
            logging.debug(f"找到路由: {path}.")
            return self.routes[path]()
        # 如果路径不存在，返回空白
        logging.debug(f"没有路由在该路径: {path}")
        return None

# 创建路由器
api_router = APIRouter()

@api_router.get("/")        # 定义注册好了根路径的 GET 请求处理函数
def root():
    logging.debug("Executing root handler.")
    return {"msg": "Hello, World!"}

# 模拟请求
print(api_router.handle_request("/"))       # 输出：{'msg': 'Hello, World!'}
print(api_router.handle_request("/123/"))   # 输出：None