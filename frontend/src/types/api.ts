export interface Pagination {
  page: number
  limit: number
  total: number
  pages: number
}

export interface ListResponse<T> {
  data: T[]
  pagination: Pagination
}

export interface ErrorResponse {
  error: {
    message: string
    type: string
    code?: string
  }
}

