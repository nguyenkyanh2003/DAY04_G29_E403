# Quyền — bonus research tools

## Tools

- `deduplicate_sources`: loại kết quả trùng theo URL chuẩn hóa hoặc tiêu đề.
- `rank_sources`: xếp kết quả theo độ phủ từ khóa và relevance score sẵn có.
- `compare_sources`: so sánh từ khóa chung/riêng của hai nguồn; không thay thế fact-check.

Các tool đều chạy local, không cần API key và không có side effect.

## YAML declarations gửi TL

```yaml
- name: deduplicate_sources
  description: "Loại kết quả nghiên cứu trùng sau khi đã dùng công cụ tìm kiếm. Dùng khi danh sách có URL hoặc tiêu đề lặp; không dùng để tìm kiếm, xếp hạng hay kiểm chứng."
  parameters:
    type: object
    properties:
      items:
        type: array
        description: "Các kết quả đã thu thập."
        items:
          type: object
          properties:
            title: {type: string}
            url: {type: string}
            source: {type: string}
            summary: {type: string}
            score: {type: number}
    required: [items]

- name: rank_sources
  description: "Xếp hạng các nguồn đã thu thập theo mức khớp truy vấn và relevance score. Chỉ dùng sau tìm kiếm; không dùng để tìm dữ liệu mới hoặc xác minh tính đúng sai."
  parameters:
    type: object
    properties:
      items:
        type: array
        description: "Các kết quả đã thu thập."
        items:
          type: object
          properties:
            title: {type: string}
            url: {type: string}
            source: {type: string}
            summary: {type: string}
            score: {type: number}
      query: {type: string, description: "Truy vấn dùng để chấm độ phủ từ khóa."}
      limit: {type: integer, minimum: 1, maximum: 20, default: 5}
    required: [items, query]

- name: compare_sources
  description: "So sánh từ khóa trong tiêu đề và tóm tắt của đúng hai nguồn đã thu thập. Dùng để thấy phần giống/khác về từ ngữ; kết quả không phải fact-check hay bằng chứng đồng thuận."
  parameters:
    type: object
    properties:
      source_a:
        type: object
        properties:
          title: {type: string}
          url: {type: string}
          source: {type: string}
          summary: {type: string}
      source_b:
        type: object
        properties:
          title: {type: string}
          url: {type: string}
          source: {type: string}
          summary: {type: string}
      max_terms: {type: integer, minimum: 1, maximum: 30, default: 12}
    required: [source_a, source_b]
```
