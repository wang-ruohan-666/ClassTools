# services/netease_service.py
import base64
import math
import time

import keyring

import requests
from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtGui import QPixmap

from MusicPlayer.common.logger import get_logger

logger = get_logger(__name__)


def _load_cookie() -> str:
    # 尝试读取分块格式
    chunks_count_str = keyring.get_password("MusicPlayer", "netease_cookie_chunks")
    if chunks_count_str:
        try:
            num_chunks = int(chunks_count_str)
            chunks = []
            for i in range(num_chunks):
                chunk_str = keyring.get_password("MusicPlayer", f"netease_cookie_{i}")
                if not chunk_str:
                    raise ValueError(f"缺少块 {i}")
                chunk_bytes = base64.b64decode(chunk_str)
                chunks.append(chunk_bytes)
            cookie_bytes = b''.join(chunks)
            return cookie_bytes.decode('utf-8')
        except Exception as e:
            logger.warning(f"分块读取失败: {e}")
    return ""


class NeteaseWorker(QObject):
    """工作类，运行在子线程中，负责所有网络请求和轮询"""
    qr_image_bytes = Signal(bytes)          # 二维码原始字节数据
    login_status = Signal(str)              # 状态文本
    notification = Signal(str)              # 提示消息
    finished = Signal()                     # 工作完成（退出线程时发送）
    save_cookie = Signal(str)               # 发送需要保存的 cookie

    def __init__(self, cookie: str, api_prefix: str):
        super().__init__()
        self.cookie = cookie
        self.api_prefix = api_prefix
        self._running = True
        self.realIP = ""

    def stop(self):
        self._running = False

    def post(self, url: str, no_caching: bool = False, data: dict = None) -> dict | None:
        if data is None:
            data = {}
        if self.cookie:
            data["cookie"] = self.cookie
        full_url = f"{self.api_prefix}{url}"
        try:
            if no_caching:
                if self.realIP:
                    resp = requests.post(f"{full_url}?timestamp={int(time.time())}&realIP={self.realIP}", data=data, timeout=10)
                else:
                    resp = requests.post(f"{full_url}?timestamp={int(time.time())}", data=data,timeout=10)
            else:
                resp = requests.post(full_url, data=data, timeout=10)
            return resp.json()
        except requests.exceptions.ConnectionError:
            self.notification.emit("网络连接失败")
            logger.error(f"请求{full_url}失败")
            return None
        except Exception as e:
            logger.exception(f"请求异常: {full_url}")
            return None

    def do_login(self):
        """执行登录流程（子线程中运行）"""
        # 1. 获取 IP地址
        headers = {
            "User-Agent": "curl/8.13.0",
            "Accept": "*/*",
        }
        try:
            ip = requests.get('https://ifconfig.co', timeout=5,headers=headers).text.strip("\n")
            self.realIP=ip
            logger.info(f"获取IP成功{ip}")
        except requests.exceptions.ConnectionError:
            logger.exception("获取IP失败")
        # 2. 获取 unikey
        resp = self.post("/login/qr/key", True)
        if not resp or resp.get("code") != 200:
            self.login_status.emit("登录失败")
            self.finished.emit()
            return
        unikey = resp.get("data", {}).get("unikey")
        if not unikey:
            self.login_status.emit("登录失败")
            self.finished.emit()
            return

        # 3. 获取二维码图片
        qr_resp = self.post("/login/qr/create", True, {"key": unikey, "qrimg": True})
        if not qr_resp or qr_resp.get("code") != 200:
            self.login_status.emit("二维码生成失败")
            self.finished.emit()
            return
        qr_img = qr_resp.get("data", {}).get("qrimg")
        if not qr_img:
            self.login_status.emit("二维码生成失败")
            self.finished.emit()
            return
        # 处理 base64 图片数据
        if ',' in qr_img and qr_img.startswith('data:'):
            qr_img = qr_img.split(',', 1)[1]
        try:
            img_bytes = base64.b64decode(qr_img)
            self.qr_image_bytes.emit(img_bytes)
        except Exception:
            self.login_status.emit("二维码解析失败")
            self.finished.emit()
            return

        # 4. 轮询扫码状态（最多 90 秒）
        self.login_status.emit("等待扫码")
        remaining = time.time()
        while time.time()-remaining <= 90 and self._running:
            time.sleep(2)
            check_resp = self.post("/login/qr/check", True, {"key": unikey})
            if not check_resp:
                continue
            code = check_resp.get("code")
            if code == 803:
                # 登录成功
                new_cookie = check_resp.get("cookie")
                if new_cookie:
                    self.login_status.emit("登录成功")
                    # 将 cookie 发给主线程保存
                    self.save_cookie.emit(new_cookie)
                else:
                    self.login_status.emit("登录失败：未获取到Cookie")
                self.finished.emit()
                return
            elif code == 802:
                self.login_status.emit("等待确认")
            # 发送剩余时间（用于 UI 倒计时）
            self.login_status.emit(str(90-int(time.time()-remaining)))
        # 超时
        logger.warning("登录超时")
        self.login_status.emit("登录超时")
        self.finished.emit()

    def do_check_cookie(self):
        """检查当前 cookie 是否有效（子线程中运行）"""
        resp = self.post("/login/status", True)
        if resp and resp.get("data", {}).get("profile") is not None:
            self.notification.emit("已登录")
            self.login_status.emit("已登录")
        else:
            self.notification.emit("cookie 无效，请重新登录")
            self.login_status.emit("未登录")
        self.finished.emit()


class NeteaseService(QObject):
    """主线程中的服务类，管理子线程并对外发送信号"""
    qr_image_ready = Signal(QPixmap)   # 二维码图片（QPixmap）
    login_status = Signal(str)         # 状态文本
    notification = Signal(str)         # 提示消息

    def __init__(self):
        super().__init__()
        self.cookie = _load_cookie()
        self.http_prefix = "http://api.ncm.qzz.io"
        self._worker_thread = None
        self._worker = None

    def _cleanup_thread(self):
        """停止并清理工作线程"""
        if self._worker_thread and self._worker_thread.isRunning():
            if self._worker:
                self._worker.stop()
            self._worker_thread.quit()
            self._worker_thread.wait()
            self._worker_thread.deleteLater()
            self._worker_thread = None
        if self._worker:
            self._worker.deleteLater()
            self._worker = None

    def _start_worker(self, target_method: str):
        """启动工作线程，执行指定方法"""
        self._cleanup_thread()
        self._worker_thread = QThread()
        self._worker = NeteaseWorker(self.cookie, self.http_prefix)
        self._worker.moveToThread(self._worker_thread)
        # 连接信号
        self._worker.login_status.connect(self.login_status)
        self._worker.qr_image_bytes.connect(self._on_qr_image_bytes)
        self._worker.notification.connect(self.notification.emit)
        self._worker.finished.connect(self._cleanup_thread)
        self._worker.save_cookie.connect(self._on_save_cookie)
        # 启动线程并调用目标方法
        if target_method == "do_login":
            self._worker_thread.started.connect(self._worker.do_login)
        elif target_method == "do_check_cookie":
            self._worker_thread.started.connect(self._worker.do_check_cookie)
        self._worker_thread.start()

    def _on_save_cookie(self, cookie: str,chunk_size_bytes=800):
        """在主线程中保存 cookie 到 keyring"""
        logger.info(f"正在保存cookie:\n{cookie}")
        cookie_bytes = cookie.encode('utf-8')
        total_bytes = len(cookie_bytes)
        num_chunks = math.ceil(total_bytes / chunk_size_bytes)

        for i in range(num_chunks):
            start = i * chunk_size_bytes
            end = min(start + chunk_size_bytes, total_bytes)
            chunk_bytes = cookie_bytes[start:end]
            chunk_str = base64.b64encode(chunk_bytes).decode('ascii')
            try:
                keyring.set_password("MusicPlayer", f"netease_cookie_{i}", chunk_str)
            except:
                logger.exception("cookie分块存储失败")
                return
        keyring.set_password("MusicPlayer", "netease_cookie_chunks", str(num_chunks))
        self.cookie = cookie
        logger.info(f"Cookie 分块保存完成，共 {num_chunks} 块，总字节 {total_bytes}")

    def _on_qr_image_bytes(self, img_bytes: bytes):
        pixmap = QPixmap()
        pixmap.loadFromData(img_bytes)
        self.qr_image_ready.emit(pixmap)

    def go_login(self):
        """启动登录流程（非阻塞）"""
        self._start_worker("do_login")

    def check_cookie(self):
        """检查当前 cookie 是否有效（非阻塞）"""
        if not self.cookie:
            self.go_login()
            return
        self._start_worker("do_check_cookie")