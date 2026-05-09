
import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '@/store';
import { api } from '@/services/api';
import { ArrowLeft, ArrowRight, Loader2 } from 'lucide-react';

export default function Survey() {
  const navigate = useNavigate();
  const { setSurvey, setAnalysis, setIsLoading } = useAppStore();
  
  const [currentProfession, setCurrentProfession] = useState('');
  const [experienceYears, setExperienceYears] = useState(0);
  const [skills, setSkills] = useState('');
  const [targetCompany, setTargetCompany] = useState('');
  const [targetPosition, setTargetPosition] = useState('');
  const [targetSalary, setTargetSalary] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!currentProfession.trim()) {
      setError('请填写当前职业/专业');
      return;
    }
    if (!skills.trim()) {
      setError('请填写核心技能');
      return;
    }
    if (!targetCompany.trim()) {
      setError('请填写目标公司');
      return;
    }
    if (!targetPosition.trim()) {
      setError('请填写目标岗位');
      return;
    }
    if (!targetSalary.trim()) {
      setError('请填写目标薪资');
      return;
    }
    
    setError('');
    setIsSubmitting(true);
    setIsLoading(true);
    
    try {
      const skillList = skills.split(/[,，、\s]+/).filter(Boolean);
      
      setSurvey({
        currentProfession,
        experienceYears,
        skills,
        targetCompany,
        targetPosition,
        targetSalary,
      });
      
      const result = await api.analysis.analyze({
        user_skills: skillList,
        user_experience: experienceYears,
        target_job: targetPosition,
        current_job: currentProfession,
        target_company: targetCompany,
      });
      
      const gapAnalysisData = result.gapAnalysis as any || {};
      const gapSkills = Array.isArray(gapAnalysisData.skills) ? gapAnalysisData.skills : [];
      console.log('[DEBUG] API response competitionAnalysis:', result.competitionAnalysis);
      console.log('[DEBUG] API response missingSkillsByGap:', result.competitionAnalysis?.missingSkillsByGap);
      const missingSkills = gapSkills
        .filter((s: any) => s.gap && (s.gap === '中' || s.gap === '大'))
        .map((s: any) => s.skill);
      const transferableSkills = gapSkills
        .filter((s: any) => s.gap && s.gap === '小')
        .map((s: any) => s.skill);
      
      const matchedJobsCount = Array.isArray(result.matchedJobs) ? result.matchedJobs.length : 0;
      const salaryData = result.salaryAnalysis?.basicStats || result.salaryAnalysis || {};
      
      setAnalysis({
        targetJob: result.targetJob || '',
        jobType: result.jobType || '',
        matchedJobs: Array.isArray(result.matchedJobs) ? result.matchedJobs : [],
        gapAnalysis: {
          skills: gapSkills,
          experience: gapAnalysisData.experience,
          education: gapAnalysisData.education,
        },
        actionPlan: result.actionPlan || {},
        transitionAnalysis: result.transitionAnalysis || {},
        competitionAnalysis: result.competitionAnalysis || {},
        salaryAnalysis: result.salaryAnalysis || {},
        skillRecommendations: {
          recommendations: result.skillRecommendations?.recommendations || [],
          skillLevels: result.skillRecommendations?.skillLevels || {},
          vueMigration: result.skillRecommendations?.vueMigration,
        },
        targetFeasibility: result.targetFeasibility || {},
        marketSkills: result.marketSkills || [],
      });
      
      navigate('/analysis');
    } catch (err) {
      console.error('分析失败:', err);
      setError('分析失败，请稍后重试');
    } finally {
      setIsSubmitting(false);
      setIsLoading(false);
    }
  };

  if (isSubmitting) {
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
                value={currentProfession}
                onChange={(e) => setCurrentProfession(e.target.value)}
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
                value={experienceYears}
                onChange={(e) => setExperienceYears(parseInt(e.target.value))}
                className="w-full px-5 py-4 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-50 outline-none transition-all text-base bg-white"
              >
                <option value={0}>应届生/无经验</option>
                <option value={1}>1年</option>
                <option value={2}>2年经验</option>
                <option value={3}>3年经验</option>
                <option value={5}>5年经验</option>
                <option value={10}>10年以上</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                核心技能
              </label>
              <textarea
                value={skills}
                onChange={(e) => setSkills(e.target.value)}
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
                  value={targetCompany}
                  onChange={(e) => setTargetCompany(e.target.value)}
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
                  value={targetPosition}
                  onChange={(e) => setTargetPosition(e.target.value)}
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
                  value={targetSalary}
                  onChange={(e) => setTargetSalary(e.target.value)}
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
