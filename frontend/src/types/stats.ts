export interface StatsSummary {
  total_requests: number
  total_prompt_tokens: number
  total_completion_tokens: number
  total_tokens: number
  total_cost: number
}

export interface StatsPeriod {
  start: string
  end: string
}

export interface DateStats {
  date: string
  requests: number
  prompt_tokens: number
  completion_tokens: number
  total_tokens: number
  cost: number
}

export interface ModelStats {
  model: string
  requests: number
  prompt_tokens: number
  completion_tokens: number
  total_tokens: number
  cost: number
}

export interface ProviderStats {
  provider: string
  requests: number
  prompt_tokens: number
  completion_tokens: number
  total_tokens: number
  cost: number
}

export interface KeyStatsResponse {
  key_id: string
  period: StatsPeriod
  summary: StatsSummary
  by_date?: DateStats[]
  by_model?: ModelStats[]
  by_provider?: ProviderStats[]
}

export interface GlobalStatsResponse {
  period: StatsPeriod
  summary: {
    total_keys: number
    active_keys: number
    total_requests: number
    total_tokens: number
    total_cost: number
  }
  by_provider: ProviderStats[]
}
