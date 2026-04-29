
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { JobMatch, SkillRecommendation } from '@/services/api';

export interface UserSurvey {
  currentProfession: string;
  experienceYears: number;
  skills: string;
  targetCompany: string;
  targetPosition: string;
  targetSalary: string;
}

export interface AbilityItem {
  dimension: string;
  requirement: string;
  current: string;
  gap: string;
}

export interface HardSkill {
  name: string;
  level: string;
  application: string;
}

export interface SoftSkill {
  name: string;
  level: string;
  importance: string;
}

export interface CompanyRequirements {
  education: string;
  educationFlexibility: string;
  experience: string;
  careerChange: string;
  certificates: string;
  '隐性偏好': string;
}

export interface GapItem {
  dimension: string;
  target: string;
  current: string;
  gap: string;
  difficulty: string;
  frequency?: number;
}

export interface ActionPath {
  shortTerm: string[];
  midTerm: string[];
  longTerm: string[];
}

export interface CompetitionAnalysis {
  supplyDemand: string;
  competitorProfile: string;
  userCompetitiveness: {
    strengths: string;
    weaknesses: string;
  };
  marketInsight?: string;
}

export interface SalaryAnalysis {
  min: number;
  max: number;
  avg: number;
  median: number;
}

export interface AnalysisResult {
  targetJob: string;
  matchedJobs: JobMatch[];
  companyStructure: string[];
  requirements: string[];
  salaryRange: string;
  salaryAnalysis: SalaryAnalysis;
  competition: string;
  gaps: string[];
  difficulty: string;
  shortTermPlan: string[];
  midTermPlan: string[];
  longTermPlan: string[];
  abilityComparison: AbilityItem[];
  actionPlans: string[];
  estimatedTime: string;
  timeReasoning: string;
  hardSkills: HardSkill[];
  softSkills: SoftSkill[];
  companyRequirements: CompanyRequirements;
  gapAnalysis: GapItem[];
  actionPath: ActionPath;
  competitionAnalysis: CompetitionAnalysis;
  promotionPath: string[];
  skillRecommendations: SkillRecommendation[];
}

interface AppState {
  survey: UserSurvey | null;
  analysis: AnalysisResult | null;
  isLoading: boolean;
  setSurvey: (survey: UserSurvey) => void;
  setAnalysis: (analysis: AnalysisResult) => void;
  setIsLoading: (loading: boolean) => void;
  reset: () => void;
}

const initialSurvey: UserSurvey = {
  currentProfession: '',
  experienceYears: 0,
  skills: '',
  targetCompany: '',
  targetPosition: '',
  targetSalary: '',
};

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      survey: initialSurvey,
      analysis: null,
      isLoading: false,

      setSurvey: (survey) => set({ survey }),
      setAnalysis: (analysis) => set({ analysis }),
      setIsLoading: (loading) => set({ isLoading: loading }),

      reset: () => set({
        survey: initialSurvey,
        analysis: null,
        isLoading: false,
      }),
    }),
    {
      name: 'career-planning-storage',
      partialize: (state) => ({
        survey: state.survey,
        analysis: state.analysis,
      }),
    }
  )
);
