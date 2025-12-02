from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    """
    Paginação customizada que retorna um formato padronizado de resposta:
    {
        "count": <total de itens>,
        "page": <página atual>,
        "page_size": <itens por página>,
        "total_pages": <total de páginas>,
        "next": <url da próxima página ou null>,
        "previous": <url da página anterior ou null>,
        "results": [...]
    }
    
    Mantém retrocompatibilidade com o formato padrão do DRF (count, next, previous, results)
    enquanto adiciona campos úteis para o frontend (page, page_size, total_pages).
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'page': self.page.number,
            'page_size': self.get_page_size(self.request),
            'total_pages': self.page.paginator.num_pages,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })
