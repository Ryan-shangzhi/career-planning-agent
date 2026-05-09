
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '@/store';
import { ArrowLeft, RefreshCw, Building2, DollarSign, TrendingUp, AlertCircle, CheckCircle2, Clock, Target, Briefcase, Star, BookOpen, ChevronDown, ChevronUp } from 'lucide-react';

export default function Analysis() {
  const navigate = useNavigate();
  const { survey, analysis, reset } = useAppStore();

  const [expandedJob, setExpandedJob] = useState<number | null>(null);
  const [showAllMissingSkills, setShowAllMissingSkills] = useState(false);

  if (!survey || !analysis) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-xl text-gray-600 mb-6">请先填写你的职业规划信息</p>
          <button
            onClick={() => navigate('/')}
            className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-8 py-4 rounded-xl font-semibold"
          >
            返回首页
          </button>
        </div>
      </div>
    );
  }

  const handleReset = () => {
    reset();
    navigate('/');
  };

  const formatSalary = (value: number) => {
    if (!value || value === 0) return '未标注';
    return `${Math.round(value / 1000)}K`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-12">
      <div className="container mx-auto px-4 max-w-5xl">
        <div className="flex items-center justify-between mb-8">
          <button
            onClick={() => navigate('/survey')}
            className="inline-flex items-center gap-2 text-gray-600 hover:text-blue-600 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            返回修改
          </button>
          <button
            onClick={handleReset}
            className="inline-flex items-center gap-2 text-gray-600 hover:text-blue-600 transition-colors"
          >
            <RefreshCw className="w-5 h-5" />
            重新规划
          </button>
        </div>

        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            你的职业规划分析报告
          </h1>
          <p className="text-xl text-gray-600">
            目标：{survey.targetCompany} · {survey.targetPosition} · {survey.targetSalary}
          </p>
        </div>

        {analysis.matchedJobs && analysis.matchedJobs.length > 0 && (
          <div className="bg-white rounded-3xl p-8 shadow-2xl mb-10">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
              <Briefcase className="w-7 h-7 text-blue-600" />
              匹配岗位推荐（基于真实职位数据）
            </h2>
            <div className="space-y-4">
              {analysis.matchedJobs.map((job, idx) => (
                <div key={job.id || idx} className="p-5 border border-gray-100 rounded-xl hover:border-blue-200 hover:shadow-md transition-all">
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h4 className="font-semibold text-gray-900">{job.title}</h4>
                        <span className={`px-2 py-1 text-xs rounded-full font-medium ${
                          job.matchStatus === '待评估' 
                            ? 'bg-gray-100 text-gray-600' 
                            : 'bg-green-100 text-green-700'
                        }`}>
                          {job.matchStatus === '待评估' 
                            ? '待评估' 
                            : `匹配度 ${job.matchScore}%`}
                        </span>
                      </div>
                      <p className="text-gray-500 text-sm mb-2">{job.companyName} · {job.location}</p>
                      <div className="flex flex-wrap gap-2">
                        {job.skills?.slice(0, 4).map((skill, skillIdx) => (
                          <span key={skillIdx} className="px-2 py-1 bg-blue-50 text-blue-600 text-xs rounded-full">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-blue-600 text-lg">
                        {job.salaryRange?.includes('面议') || job.salaryRange === '未提供' ? '未标注' : job.salaryRange}
                      </p>
                      <p className="text-gray-500 text-xs">{job.experienceRequirement} · {job.educationRequirement}</p>
                    </div>
                  </div>
                  {/* JD 详情 */}
                  {job.description && (
                    <div className="mt-3 pt-3 border-t border-gray-100">
                      <button
                        onClick={() => setExpandedJob(expandedJob === job.id ? null : job.id)}
                        className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
                      >
                        {expandedJob === job.id ? '▼ 收起详情' : '▶ 查看JD详情'}
                      </button>
                      {expandedJob === job.id && (
                        <div className="mt-2 p-3 bg-gray-50 rounded-lg text-sm text-gray-700 leading-relaxed whitespace-pre-line max-h-60 overflow-y-auto">
                          {job.description}
                          {job.sourceUrl && (
                            <a
                              href={job.sourceUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-block mt-2 text-blue-600 hover:text-blue-800 text-xs"
                            >
                              🔗 查看原链接（{job.source}）
                            </a>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="grid md:grid-cols-3 gap-6 mb-10">
          <div className="bg-white rounded-2xl p-6 shadow-xl">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-xl flex items-center justify-center">
                <Building2 className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-semibold text-gray-900">市场薪资分析</h3>
            </div>
            {(() => {
              const validSalaryCount = (analysis.salaryAnalysis?.validCount || 0);
              const targetSalary = survey.targetSalary;
              if (validSalaryCount < 10) {
                return (
                  <div>
                    <div className="text-lg font-semibold text-gray-700 mb-3">样本薪资分布</div>
                    <div className="border-t border-b border-gray-200 py-2 my-3">
                      <p className="text-sm text-gray-600">当前样本中薪资标注的岗位有限</p>
                      {targetSalary && (
                        <div className="mt-3">
                          <p className="text-sm font-medium text-indigo-700">你的目标 {targetSalary} 处于高级/资深区间</p>
                          <p className="text-xs text-gray-500 mt-1">（参考：样本中高级岗 25K-40K）</p>
                        </div>
                      )}
                    </div>
                  </div>
                );
              }
              return (
                <div>
                  <div className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-3">
                    {formatSalary(analysis.salaryAnalysis?.avg || 0)}
                  </div>
                  <p className="text-sm text-gray-600 mb-2">
                    薪资范围：{formatSalary(analysis.salaryAnalysis?.min || 0)} - {formatSalary(analysis.salaryAnalysis?.max || 0)}
                  </p>
                  <p className="text-sm text-gray-600">中位数：{formatSalary(analysis.salaryAnalysis?.median || 0)}</p>
                </div>
              );
            })()}
          </div>

          <div className="bg-white rounded-2xl p-6 shadow-xl">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-amber-500 rounded-xl flex items-center justify-center">
                <DollarSign className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-semibold text-gray-900">目标薪资</h3>
            </div>
            <div className="text-3xl font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent mb-3">
              {survey.targetSalary}
            </div>
            <p className="text-sm text-gray-600">{analysis.competitionAnalysis?.supplyDemand || '市场竞争分析中'}</p>
          </div>

          <div className="bg-white rounded-2xl p-6 shadow-xl">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-semibold text-gray-900">达成难度</h3>
            </div>
            <p className="text-lg text-gray-800 font-semibold">{analysis.targetFeasibility?.difficulty || '中等'}</p>
          </div>
        </div>

        <div className="bg-white rounded-3xl p-8 shadow-2xl mb-10">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <Target className="w-7 h-7 text-blue-600" />
            岗位招聘要求（来自真实职位）
          </h2>
          <div className="grid md:grid-cols-2 gap-4">
            {analysis.matchedJobs.slice(0, 4).map((job, idx) => (
              <div key={idx} className="flex items-start gap-3 p-4 bg-gray-50 rounded-xl">
                <CheckCircle2 className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
                <span className="text-gray-700">{job.companyName} - {job.title} ({job.salaryRange?.includes('面议') || job.salaryRange === '未提供' ? '未标注' : job.salaryRange})</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-3xl p-8 shadow-2xl mb-10">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <Target className="w-7 h-7 text-blue-600" />
            一、目标岗位能力图谱
          </h2>
          
          <div className="mb-8">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">1. 你的技能（基于输入）</h3>
            <div className="p-4 bg-blue-50 rounded-xl">
              <div className="flex flex-wrap gap-3">
                {Object.entries(analysis.skillRecommendations?.skillLevels || {}).map(([skill, level]) => (
                  <div key={skill} className="inline-flex items-center gap-2 px-3 py-2 bg-white rounded-lg shadow-sm">
                    <span className="font-medium text-gray-800">{skill}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      level === '精通' ? 'bg-green-100 text-green-700' :
                      level === '熟练' ? 'bg-blue-100 text-blue-700' :
                      level === '了解' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {level}
                    </span>
                  </div>
                ))}
              </div>
              {Object.keys(analysis.skillRecommendations?.skillLevels || {}).length === 0 && (
                <p className="text-gray-500">暂无技能数据</p>
              )}
              {analysis.skillRecommendations?.impliedSkills && Object.keys(analysis.skillRecommendations.impliedSkills).length > 0 && (
                <div className="mt-4 pt-4 border-t border-blue-200">
                  <p className="text-sm text-gray-500 mb-2">隐含基础技能：</p>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(analysis.skillRecommendations.impliedSkills).map(([skill, level]) => (
                      <div key={skill} className="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 rounded text-xs">
                        <span className="text-gray-600">{skill}</span>
                        <span className="text-gray-400">({String(level)})</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
          
          <div>
            <h3 className="text-xl font-semibold text-gray-800 mb-4">2. 目标岗位常见技能</h3>
            <div className="p-4 bg-purple-50 rounded-xl">
              <p className="text-sm text-gray-600 mb-3">以下是样本中出现频率较高的技能，可作为学习参考：</p>
              <div className="flex flex-wrap gap-2">
                {(analysis.marketSkills?.length ? analysis.marketSkills : ['Angular', '性能优化', '微前端', 'TypeScript进阶', 'Node.js', 'Webpack']).slice(0, 6).map((skill) => (
                  <span key={skill} className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm">
                    {skill}
                  </span>
                ))}
              </div>
              {analysis.marketSkills?.length === 0 && (
                <p className="text-xs text-gray-400 mt-2">注：样本数据有限，以上为通用技能参考</p>
              )}
              {analysis.marketSkills?.length > 0 && analysis.marketSkills?.length < 10 && (
                <p className="text-xs text-gray-400 mt-2">注：样本数据较少，供参考学习</p>
              )}
            </div>
          </div>
        </div>

        <div className="bg-white rounded-3xl p-8 shadow-2xl mb-10">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <Building2 className="w-7 h-7 text-indigo-600" />
            二、目标公司/行业人员要求
          </h2>
          
          <div className="grid md:grid-cols-2 gap-6">
            <div className="p-4 bg-indigo-50 rounded-xl">
              <h3 className="font-semibold text-gray-800 mb-2">1. 学历门槛</h3>
              <p className="text-gray-700 mb-2">{analysis.gapAnalysis.education?.required || '本科'}</p>
              <p className="text-gray-600 text-sm">放宽空间：视具体公司而定</p>
            </div>

            <div className="p-4 bg-indigo-50 rounded-xl">
              <h3 className="font-semibold text-gray-800 mb-2">2. 经验要求</h3>
              <p className="text-gray-700 mb-1">
                <span className="font-medium">你的经验：</span>{survey.experienceYears}年
              </p>
              <p className="text-gray-700 mb-2">
                <span className="font-medium">样本中位数要求：</span>{analysis.gapAnalysis.experience?.market_required || '不限'}
              </p>
            </div>

            <div className="p-4 bg-indigo-50 rounded-xl">
              <h3 className="font-semibold text-gray-800 mb-2">3. 证书/资质</h3>
              <p className="text-gray-700">暂无特殊要求</p>
            </div>

            <div className="p-4 bg-indigo-50 rounded-xl">
              <h3 className="font-semibold text-gray-800 mb-2">4. 隐性偏好</h3>
              <p className="text-gray-700">大厂背景优先、开源项目经验加分</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-3xl p-8 shadow-2xl mb-10">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <AlertCircle className="w-7 h-7 text-orange-500" />
            三、用户差距分析表
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="bg-gray-100">
                  <th className="border border-gray-300 px-4 py-3 text-left text-sm font-semibold text-gray-700">技能</th>
                  <th className="border border-gray-300 px-4 py-3 text-left text-sm font-semibold text-gray-700">目标要求</th>
                  <th className="border border-gray-300 px-4 py-3 text-left text-sm font-semibold text-gray-700">用户现状</th>
                  <th className="border border-gray-300 px-4 py-3 text-left text-sm font-semibold text-gray-700">差距</th>
                  <th className="border border-gray-300 px-4 py-3 text-left text-sm font-semibold text-gray-700">出现频率</th>
                  <th className="border border-gray-300 px-4 py-3 text-left text-sm font-semibold text-gray-700">补足难度</th>
                </tr>
              </thead>
              <tbody>
                {analysis.gapAnalysis.skills?.map((item, idx) => (
                  <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className="border border-gray-300 px-4 py-3 text-sm text-gray-700 font-medium">{item.skill}</td>
                    <td className="border border-gray-300 px-4 py-3 text-sm text-gray-700">{item.requiredLevel}</td>
                    <td className="border border-gray-300 px-4 py-3 text-sm text-gray-700">{item.userLevel}</td>
                    <td className={`border border-gray-300 px-4 py-3 text-sm font-medium ${
                      item.gap === '小' ? 'text-green-600' : item.gap === '中' ? 'text-yellow-600' : 'text-red-600'
                    }`}>{item.gap}</td>
                    <td className="border border-gray-300 px-4 py-3 text-sm">
                      {(() => {
                        const freq = item.frequency || '-';
                        const freqMap: Record<string, { text: string; color: string; emoji: string }> = {
                          '高频': { text: '刚需技能', color: '#ff4d4f', emoji: '🔥' },
                          '中频': { text: '主流技能', color: '#1890ff', emoji: '📌' },
                          '低频': { text: '专项技能', color: '#722ed1', emoji: '⭐' },
                          '样本不足': { text: '进阶可选', color: '#8c8c8c', emoji: '📚' },
                        };
                        const map = freqMap[freq];
                        if (map) {
                          return (
                            <span style={{ color: map.color }}>
                              {map.emoji} {map.text}
                            </span>
                          );
                        }
                        return freq;
                      })()}
                    </td>
                    <td className={`border border-gray-300 px-4 py-3 text-sm ${
                      item.difficulty === '小' ? 'text-green-600' : item.difficulty === '中' ? 'text-yellow-600' : 'text-red-600'
                    }`}>{item.difficulty}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {analysis.skillRecommendations?.recommendations && analysis.skillRecommendations.recommendations.length > 0 && (
          <div className="bg-white rounded-3xl p-8 shadow-2xl mb-10">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
              <BookOpen className="w-7 h-7 text-teal-600" />
              技能学习推荐
            </h2>
            <div className="grid md:grid-cols-2 gap-4">
              {analysis.skillRecommendations.recommendations.map((rec, idx) => (
                <div key={idx} className="p-4 bg-teal-50 rounded-xl">
                  <div className="flex items-center gap-2 mb-2">
                    <Star className="w-5 h-5 text-teal-600" />
                    <h4 className="font-semibold text-gray-800">{rec.skill}</h4>
                  </div>
                  <p className="text-sm text-gray-600 mb-1">推荐资源：{rec.platform}</p>
                  <p className="text-sm text-gray-600 mb-1">预计时间：{rec.duration}</p>
                  <p className="text-sm text-gray-600">难度：{rec.difficulty}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="bg-white rounded-3xl p-8 shadow-2xl mb-10">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <CheckCircle2 className="w-7 h-7 text-green-600" />
            四、行动路径
          </h2>
          
          <div className="mb-8">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">短期（1-3个月）</h3>
            <div className="space-y-4">
              {(analysis.actionPlan?.shortTerm?.items || []).map((action, idx) => (
                <div key={idx} className="flex items-start gap-3 p-4 bg-green-50 rounded-xl">
                  <CheckCircle2 className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700 whitespace-pre-wrap">{action}</span>
                </div>
              ))}
            </div>
          </div>
          
          <div className="mb-8">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">中期（3-6个月）</h3>
            <div className="space-y-4">
              {(analysis.actionPlan?.mediumTerm?.items || []).map((action, idx) => (
                <div key={idx} className="flex items-start gap-3 p-4 bg-blue-50 rounded-xl">
                  <CheckCircle2 className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700 whitespace-pre-wrap">{action}</span>
                </div>
              ))}
            </div>
          </div>
          
          <div>
            <h3 className="text-xl font-semibold text-gray-800 mb-4">长期（6-12个月）</h3>
            <div className="space-y-4">
              {(analysis.actionPlan?.longTerm?.items || []).map((action, idx) => (
                <div key={idx} className="flex items-start gap-3 p-4 bg-purple-50 rounded-xl">
                  <CheckCircle2 className="w-5 h-5 text-purple-500 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700 whitespace-pre-wrap">{action}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="bg-white rounded-3xl p-8 shadow-2xl mb-10">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <TrendingUp className="w-7 h-7 text-red-600" />
            五、竞争力度分析
          </h2>
          
          <div className="grid md:grid-cols-2 gap-6">
            <div className="p-4 bg-red-50 rounded-xl">
              <h3 className="font-semibold text-gray-800 mb-2">1. 该岗位供需情况</h3>
              <p className="text-gray-700">{analysis.competitionAnalysis?.supplyDemand || '暂无数据'}</p>
            </div>
            
            <div className="p-4 bg-red-50 rounded-xl">
              <h3 className="font-semibold text-gray-800 mb-2">2. 竞争者画像</h3>
              <p className="text-gray-700 text-sm">{analysis.competitionAnalysis?.competitorProfile || '暂无数据'}</p>
            </div>
            
            <div className="p-4 bg-red-50 rounded-xl">
              <h3 className="font-semibold text-gray-800 mb-2">3. 你的优势</h3>
              <p className="text-gray-700 text-sm">{analysis.competitionAnalysis?.userAdvantage || '暂无数据'}</p>
            </div>
            
            <div className="p-4 bg-red-50 rounded-xl">
              <h3 className="font-semibold text-gray-800 mb-2">4. 需要提升</h3>
              <p className="text-gray-700 text-sm mb-3">{analysis.competitionAnalysis?.userDisadvantage || '暂无数据'}</p>
              {(() => {
                const missingList = analysis.competitionAnalysis?.missingSkillsByGap || { 大: [], 中: [] };
                console.log('[DEBUG] missingSkillsByGap:', missingList);
                const allSkills = [...missingList.大, ...missingList.中];
                console.log('[DEBUG] allSkills:', allSkills, 'length:', allSkills.length);
                if (allSkills.length === 0) return null;
                const displaySkills = showAllMissingSkills ? allSkills : allSkills.slice(0, 3);
                return (
                  <div className="mt-2">
                    <div className="flex flex-wrap gap-2 mb-2">
                      {missingList.大.map((skill, i) => (
                        <span key={i} className="px-2 py-1 bg-red-100 text-red-700 rounded text-xs font-medium">
                          {skill} (差距大)
                        </span>
                      ))}
                      {missingList.中.map((skill, i) => (
                        <span key={i} className="px-2 py-1 bg-orange-100 text-orange-700 rounded text-xs font-medium">
                          {skill} (差距中)
                        </span>
                      ))}
                    </div>
                    {allSkills.length > 3 && (
                      <button
                        onClick={() => setShowAllMissingSkills(!showAllMissingSkills)}
                        className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800"
                      >
                        {showAllMissingSkills ? (
                          <><ChevronUp className="w-4 h-4" />收起</>
                        ) : (
                          <><ChevronDown className="w-4 h-4" />还有 {allSkills.length - 3} 项</>
                        )}
                      </button>
                    )}
                  </div>
                );
              })()}
            </div>
          </div>
          
          {analysis.competitionAnalysis?.marketInsight && (
            <div className="mt-6 p-4 bg-blue-50 rounded-xl">
              <h3 className="font-semibold text-gray-800 mb-2">市场洞察</h3>
              <p className="text-gray-700">{analysis.competitionAnalysis.marketInsight}</p>
            </div>
          )}
        </div>

        <div className="bg-white rounded-3xl p-8 shadow-2xl mb-10">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <Clock className="w-7 h-7 text-purple-600" />
            达成时间评估
          </h2>
          <div className="space-y-4">
            <div className="p-5 bg-purple-50 rounded-2xl">
              <div className="text-2xl font-bold text-purple-700 mb-3">{analysis.actionPlan?.timeEstimate?.timeRange || '6-12个月'}</div>
              <div className="text-gray-700 whitespace-pre-line">{analysis.actionPlan?.timeEstimate?.reasoning || '正在计算中...'}</div>
            </div>
          </div>
        </div>

        <div className="mt-12 text-center">
          <button
            onClick={handleReset}
            className="inline-flex items-center gap-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-10 py-5 rounded-2xl text-lg font-semibold shadow-xl hover:shadow-2xl transform hover:-translate-y-1 transition-all duration-300"
          >
            <RefreshCw className="w-6 h-6" />
            为自己做一份新的规划
          </button>
        </div>
      </div>
    </div>
  );
}
