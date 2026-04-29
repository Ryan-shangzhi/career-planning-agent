import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '@/store';
import { api, EnhancedAnalysisResponse } from '@/services/api';
import { ArrowLeft, ArrowRight, Loader2 } from 'lucide-react';

export default function Survey() {
  const navigate = useNavigate();
  const { survey, setSurvey, setAnalysis, setIsLoading, isLoading } = useAppStore();
  
  const [formData, setFormData] = useState({
    currentProfession: survey?.currentProfession || '',
    experienceYears: survey?.experienceYears || 0,
    skills: survey?.skills || '',
    targetCompany: survey?.targetCompany || '',
    targetPosition: survey?.targetPosition || '',
    targetSalary: survey?.targetSalary || '',
  });

  const [error, setError] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    setIsLoading(true);
    setError('');
    
    try {
      setSurvey(formData);
      
      const analysisRequest = {
        user_skills: formData.skills.split(/[,，、\s]+/).filter(Boolean),
        user_experience: formData.experienceYears,
        target_job: formData.targetPosition,
        target_company: formData.targetCompany,
      };
      
      const result: any = await api.analysis.analyze(analysisRequest);
      
      const missingSkills = result.gapAnalysis?.skills
        ?.filter((s: any) => s.gap === '缺口')
        .map((s: any) => s.skill) || [];
      
      const analysis = {
        targetJob: result.targetJob,
        matchedJobs: result.matchedJobs,
        companyStructure: [],
        requirements: result.matchedJobs?.length > 0 
          ? result.matchedJobs.slice(0, 3).map((j: any) => `${j.companyName} - ${j.title} (${j.salaryRange})`)
          : ['暂无匹配岗位数据'],
        salaryRange: `${Math.round((result.salaryAnalysis?.avg || 0) / 1000)}K-${Math.round((result.salaryAnalysis?.max || 0) / 1000)}K`,
        salaryAnalysis: result.salaryAnalysis || {},
        competition: result.competitionAnalysis?.supplyDemand || '',
        gaps: missingSkills,
        difficulty: missingSkills.length > 3 ? '较大' : missingSkills.length > 0 ? '中等' : '较小',
        shortTermPlan: result.actionPlan?.shortTerm || [],
        midTermPlan: result.actionPlan?.mediumTerm || [],
        longTermPlan: result.actionPlan?.longTerm || [],
        abilityComparison: (result.gapAnalysis?.skills || []).map((s: any) => ({
          dimension: s.skill,
          requirement: s.required ? '精通' : '了解',
          current: s.userHas ? '精通' : '了解',
          gap: s.gap,
        })),
        actionPlans: [
          ...(result.actionPlan?.shortTerm || []),
          ...(result.actionPlan?.mediumTerm || []),
          ...(result.actionPlan?.longTerm || []),
        ],
        estimatedTime: missingSkills.length > 3 ? '12-18个月' : missingSkills.length > 0 ? '6-12个月' : '3-6个月',
        timeReasoning: `基于${result.matchedJobs?.length || 0}个匹配岗位分析，需补充${missingSkills.length}项核心技能`,
        hardSkills: (result.gapAnalysis?.skills || []).slice(0, 8).map((s: any) => ({
          name: s.skill,
          level: s.userHas ? '精通' : '入门',
          application: '工作中常用',
        })),
        softSkills: [],
        companyRequirements: {
          education: result.gapAnalysis?.education?.required || '',
          educationFlexibility: '中等',
          experience: result.gapAnalysis?.experience?.required || '',
          careerChange: '可行',
          certificates: '',
          '隐性偏好': '',
        },
        gapAnalysis: (result.gapAnalysis?.skills || []).map((s: any) => ({
          dimension: s.skill,
          target: s.required ? '精通' : '了解',
          current: s.userHas ? '精通' : '了解',
          gap: s.gap,
          difficulty: s.gap === '达标' ? '小' : s.userHas ? '中' : '大',
          frequency: s.frequency,
        })),
        actionPath: {
          shortTerm: result.actionPlan?.shortTerm || [],
          midTerm: result.actionPlan?.mediumTerm || [],
          longTerm: result.actionPlan?.longTerm || [],
        },
        competitionAnalysis: {
          supplyDemand: result.competitionAnalysis?.supplyDemand || '',
          competitorProfile: result.competitionAnalysis?.competitorProfile || '',
          userCompetitiveness: {
            strengths: result.competitionAnalysis?.userAdvantage || '',
            weaknesses: result.competitionAnalysis?.userDisadvantage || '',
          },
          marketInsight: result.competitionAnalysis?.marketInsight || '',
        },
        promotionPath: [],
        skillRecommendations: result.skillRecommendations?.recommendations || [],
      };
      
      setAnalysis(analysis);
      navigate('/analysis');
    } catch (err) {
      console.error('分析失败:', err);
      setError('分析失败，请稍后重试');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (field: string, value: string | number) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-16 h-16 text-blue-600 animate-spin mx-auto mb-6" />
          <h2 className="text-2xl font-bold text-gray-800 mb-3">正在分析中...</h2>
          <p className="text-gray-600">正在搜索岗位信息，为你生成专属规划方案</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-12">
      <div className="container mx-auto px-4 max-w-3xl">
        <button
          onClick={() => navigate('/')}
          className="inline-flex items-center gap-2 text-gray-600 hover:text-blue-600 mb-8 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          返回首页
        </button>

        <div className="bg-white rounded-3xl shadow-2xl p-8 md:p-12">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            了解你的现状
          </h1>
          <p className="text-gray-600 mb-10">
            填写以下信息，让我更好地为你制定职业规划
          </p>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-600">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-8">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                当前职业/专业
              </label>
              <input
                type="text"
                value={formData.currentProfession}
                onChange={(e) => handleInputChange('currentProfession', e.target.value)}
                placeholder="例如：前端开发工程师 / 计算机科学与技术"
                className="w-full px-5 py-4 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-50 outline-none transition-all text-base"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                工作经验年限
              </label>
              <select
                value={formData.experienceYears}
                onChange={(e) => handleInputChange('experienceYears', parseInt(e.target.value))}
                className="w-full px-5 py-4 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-50 outline-none transition-all text-base bg-white"
              >
                {[0, 1, 2, 3, 5, 10].map((year) => (
                  <option key={year} value={year}>
                    {year === 0 ? '应届生/无经验' : `${year}年${year === 1 ? '' : '经验'}`}
                  </option>
                ))}
                <option value={15}>10年以上</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                核心技能
              </label>
              <textarea
                value={formData.skills}
                onChange={(e) => handleInputChange('skills', e.target.value)}
                placeholder="例如：JavaScript、React、Node.js、项目管理..."
                rows={4}
                className="w-full px-5 py-4 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-50 outline-none transition-all text-base resize-none"
                required
              />
            </div>

            <hr className="border-gray-100" />

            <div className="pt-2">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">你的目标</h3>

              <div className="mb-6">
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  目标公司
                </label>
                <input
                  type="text"
                  value={formData.targetCompany}
                  onChange={(e) => handleInputChange('targetCompany', e.target.value)}
                  placeholder="例如：阿里巴巴、腾讯、字节跳动..."
                  className="w-full px-5 py-4 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-50 outline-none transition-all text-base"
                  required
                />
              </div>

              <div className="mb-6">
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  目标岗位
                </label>
                <input
                  type="text"
                  value={formData.targetPosition}
                  onChange={(e) => handleInputChange('targetPosition', e.target.value)}
                  placeholder="例如：高级前端工程师、产品经理..."
                  className="w-full px-5 py-4 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-50 outline-none transition-all text-base"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  目标薪资（月薪）
                </label>
                <input
                  type="text"
                  value={formData.targetSalary}
                  onChange={(e) => handleInputChange('targetSalary', e.target.value)}
                  placeholder="例如：25K、30K、50K"
                  className="w-full px-5 py-4 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-50 outline-none transition-all text-base"
                  required
                />
              </div>
            </div>

            <div className="pt-4">
              <button
                type="submit"
                className="w-full flex items-center justify-center gap-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-10 py-5 rounded-2xl text-lg font-semibold shadow-xl hover:shadow-2xl transform hover:-translate-y-1 transition-all duration-300"
              >
                开始分析
                <ArrowRight className="w-6 h-6" />
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
