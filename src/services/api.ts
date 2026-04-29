function getBaseURL(): string {
  if (import.meta.env.DEV) {
    return '/api';
  }
  if (typeof window !== 'undefined') {
    const host = window.location.hostname;
    const protocol = window.location.protocol;
    if (host.includes('trae.cn') || host.includes('agent-sandbox')) {
      return `${protocol}//${host}/api`;
    }
  }
  return '/api';
}

const BASE_URL = getBaseURL();

export interface Job {
  id: number;
  title: string;
  company_name: string;
  industry: string | null;
  location: string | null;
  salary_min: number | null;
  salary_max: number | null;
  experience_requirement: string | null;
  education_requirement: string | null;
  description: string | null;
  skills: string | null;
  source: string | null;
  created_at: string;
}

export interface JobMatch {
  id: number;
  title: string;
  company_name: string;
  location: string | null;
  salary_range: string;
  experience_requirement: string | null;
  education_requirement: string | null;
  skills: string[];
  match_score: number;
}

export interface SkillRecommendation {
  skill: string;
  platform: string;
  duration: string;
  difficulty: string;
}

export interface AnalysisRequest {
  user_id?: number;
  user_skills: string[];
  user_experience: number;
  target_job: string;
  target_company?: string;
}

export interface GapAnalysis {
  skill: string;
  required: boolean;
  user_has: boolean;
  gap: string;
  frequency: number;
}

export interface EnhancedAnalysisResponse {
  target_job: string;
  matched_jobs: JobMatch[];
  gap_analysis: {
    skills: GapAnalysis[];
    experience: {
      required: string;
      user: number;
      gap: number;
    };
    education: {
      required: string;
      market_trend: string;
    };
  };
  action_plan: {
    short_term: string[];
    medium_term: string[];
    long_term: string[];
  };
  competition_analysis: {
    supply_demand: string;
    competitor_profile: string;
    user_advantage: string;
    user_disadvantage: string;
    market_insight: string;
  };
  salary_analysis: {
    min: number;
    max: number;
    avg: number;
    median: number;
  };
  skill_recommendations: {
    recommendations: SkillRecommendation[];
  };
}

export interface AnalysisResponse {
  target_job: string;
  gap_analysis: {
    skills: {
      skill: string;
      required: boolean;
      user_has: boolean;
      gap: string;
    }[];
    experience: {
      required: string;
      user: number;
    };
  };
  action_plan: {
    short_term: string[];
    medium_term: string[];
    long_term: string[];
  };
  competition_analysis: {
    supply_demand: string;
    competitor_profile: string;
    user_advantage: string;
    user_disadvantage: string;
  };
}

async function fetchWithFallback(url: string, options?: RequestInit): Promise<Response> {
  try {
    const response = await fetch(url, options);
    return response;
  } catch (error) {
    throw new Error('网络请求失败，请检查网络连接');
  }
}

export const api = {
  jobs: {
    async getJobs(keyword?: string, city?: string, limit: number = 20): Promise<Job[]> {
      if (!keyword && !city) {
        const url = `${BASE_URL}/jobs?limit=${limit}`;
        const response = await fetchWithFallback(url);
        if (!response.ok) {
          const errorText = await response.text().catch(() => '');
          throw new Error(`获取职位列表失败: ${response.status} - ${errorText || '未知错误'}`);
        }
        return response.json();
      }

      const response = await fetchWithFallback(`${BASE_URL}/jobs/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          keyword: keyword?.trim() || null,
          city: city?.trim() || null,
          limit
        }),
      });
      
      if (!response.ok) {
        const errorText = await response.text().catch(() => '');
        throw new Error(`获取职位列表失败: ${response.status} - ${errorText || '未知错误'}`);
      }
      return response.json();
    },

    async getJob(id: number): Promise<Job> {
      const response = await fetchWithFallback(`${BASE_URL}/jobs/${id}`);
      if (!response.ok) throw new Error('获取职位详情失败');
      return response.json();
    },

    async createJob(job: Omit<Job, 'id' | 'created_at'>): Promise<{ id: number; message: string }> {
      const response = await fetchWithFallback(`${BASE_URL}/jobs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(job),
      });
      if (!response.ok) throw new Error('创建职位失败');
      return response.json();
    },

    async deleteJob(id: number): Promise<{ message: string }> {
      const response = await fetchWithFallback(`${BASE_URL}/jobs/${id}`, { method: 'DELETE' });
      if (!response.ok) throw new Error('删除职位失败');
      return response.json();
    },
  },

  crawl: {
    async crawlJobs(keyword: string, city: string = '北京', pages: number = 1): Promise<{ message: string }> {
      const response = await fetchWithFallback(`${BASE_URL}/crawl`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          keyword,
          city,
          pages
        }),
      });
      if (!response.ok) throw new Error('爬取失败');
      return response.json();
    },
  },

  analysis: {
    async analyze(request: AnalysisRequest): Promise<EnhancedAnalysisResponse> {
      const response = await fetchWithFallback(`${BASE_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      });
      if (!response.ok) {
        const errorText = await response.text().catch(() => '');
        throw new Error(`分析失败: ${response.status} - ${errorText || '未知错误'}`);
      }
      return response.json();
    },
  },

  health: {
    async check(): Promise<{ message: string }> {
      const response = await fetchWithFallback('/');
      if (!response.ok) throw new Error('服务不可用');
      return response.json();
    },
  },
};
