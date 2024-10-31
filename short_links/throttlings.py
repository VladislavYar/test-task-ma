from datetime import datetime
from datetime import timedelta


class Throttling:
    """Класс троттлинга запросов.

    Attributes:
        max_count_requests (int): максимальное количесво запросов.
        duration (int): период запросов.
        blocking_time (int): время блокировки.
    """

    max_count_requests = 5
    duration = 10
    blocking_time = 10

    def __init__(self) -> None:
        """Инициализация истории обращений."""
        self.history: list[dict[str, datetime]] = []
        self.blocking_ip: dict[str, datetime] = {}

    def _check_ip_in_blocked(self, ip: str) -> bool:
        """Проверка блокировки ip.

        Args:
            ip (str): ip пользователя.
        Returns:
            bool: флаг блокировки ip.
        """
        time = self.blocking_ip.get(ip)
        if not time:
            return False
        if self.now < (time + timedelta(seconds=self.blocking_time)):
            return True
        self.blocking_ip.pop(ip)
        return False

    def refresh_history(self, ip: str) -> bool:
        """Обновление истории.

        Args:
            ip (str): ip пользователя.
        Returns:
            bool: флаг блокировки ip.
        """
        self.now = datetime.now()
        if self._check_ip_in_blocked(ip):
            return True

        refresh_history = [{ip: self.now}]
        count_of_ip_requests = 1
        time_clear_history = self.now - timedelta(seconds=self.duration)
        for data in self.history:
            if list(data.values())[0] <= time_clear_history:
                continue
            refresh_history.append(data)
            if list(data.keys())[0] == ip:
                count_of_ip_requests += 1

        self.history = refresh_history
        if count_of_ip_requests <= self.max_count_requests:
            return False
        self.blocking_ip[ip] = self.now
        return True
