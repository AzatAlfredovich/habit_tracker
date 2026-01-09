from rest_framework.pagination import PageNumberPagination


class HabitPagination(PageNumberPagination):
    page_size = 5  # 5 привычек на страницу
    page_size_query_param = (
        "page_size"  # параметр для изменения размера страницы (опционально)
    )
    max_page_size = 10  # максимум 10 привычек на страницу
