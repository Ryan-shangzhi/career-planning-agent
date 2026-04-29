
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '@/store';
import { ArrowLeft, RefreshCw, Building2, DollarSign, TrendingUp, AlertCircle, CheckCircle2, Clock, Target, Briefcase, Star, BookOpen } from 'lucide-react';

export default function Analysis() {
  const navigate = useNavigate();
  const { survey, analysis, reset } = useAppStore();

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
    return `${Math.round(value / 1000)}`;
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
                        <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full font-medium">
                          匹配度 {job.match_score}%
                        </span>
                      </div>
                      <p className="text-gray-500 text-sm mb-2">{job.company_name} · {job.location}</p>
                      <div className="flex flex-wrap gap-2">
                        {job.skills?.slice(0, 4).map((skill, skillIdx) => (
                          <span key={skillIdx} className="px-2 py-1 bg-blue-50 text-blue-600 text-xs rounded-full">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-blue-600 text-lg">{job.salary_range}</p>
                      <p className="text-gray-500 text-xs">{job.experience_requirement} · {job.education_requirement}</p>
                    </div>
                  </div>
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
            <div className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-3">
              {formatSalary(analysis.salaryAnalysis?.avg || 0)}
            </div>
            <p className="text-sm text-gray-600 mb-2">
              薪资范围：{formatSalary(analysis.salaryAnalysis?.min || 0)} - {formatSalary(analysis.salaryAnalysis?.max || 0)}
            </p>
            <p className="text-sm text-gray-600">中位数：{formatSalary(analysis.salaryAnalysis?.median || 0)}</p>
          </div>

          <div className="bg-white rounded-2xl p-6 shadow-xl">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-amber-500 rounded-xl flex items-center justify-center">
                <DollarSign className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-semibold text-gray-900">目标薪资</h3>
            </div>
            <div className="text-3xl font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent mb-3">
              {analysis.salaryRange}
            </div>
            <p className="text-sm text-gray-600">{analysis.competition}</p>
          </div>

          <div className="bg-white rounded-2xl p-6 shadow-xl">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-semibold text-gray-900">达成难度</h3>
            </div>
            <p className="text-lg text-gray-800 font-semibold">{analysis.difficulty}</p>
          </div>
        </div>

        <div className="bg-white rounded-3xl p-8 shadow-2xl mb-10">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <Target className="w-7 h-7 text-blue-600" />
            岗位招聘要求（来自真实职位）
          </h2>
          <div className="grid md:grid-cols-2 gap-4">
            {analysis.requirements.map((req, idx) => (
              <div key={idx} className="flex items-start gap-3 p-4 bg-gray-50 rounded-xl">
                <CheckCircle2 className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
                <span className="text-gray-700">{req}</span>
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
            <h3 className="text-xl font-semibold text-gray-800 mb-4">1. 硬技能清单（基于职位数据分析）</h3>
            <div className="p-4 bg-blue-50 rounded-xl">
              <div className="flex flex-wrap gap-3">
                {analysis.hardSkills.map((skill, idx) => (
                  <div key={idx} className="inline-flex items-center gap-2 px-3 py-2 bg-white rounded-lg shadow-sm">
                    <span className="font-medium text-gray-800">{skill.name}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      skill.level === '精通' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                    }`}>
                      {skill.level}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
          
          <div>
            <h3 className="text-xl font-semibold text-gray-800 mb-4">2. 软技能清单</h3>
            <div className="p-4 bg-green-50 rounded-xl">
              {analysis.softSkills.length > 0 ? (
                <div className="flex flex-wrap gap-3">
                  {analysis.softSkills.map((skill, idx) => (
                    <span key={idx} className="inline-block mr-4 mb-2">
                      {skill.name}（{skill.level}）
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">根据岗位分析，建议培养：沟通协作、问题解决、学习能力、项目管理等软技能</p>
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
              <p className="text-gray-700 mb-2">{analysis.companyRequirements.education}</p>
              <p className="text-gray-600 text-sm">放宽空间：{analysis.companyRequirements.educationFlexibility}</p>
            </div>
            
            <div className="p-4 bg-indigo-50 rounded-xl">
              <h3 className="font-semibold text-gray-800 mb-2">2. 经验要求</h3>
              <p className="text-gray-700 mb-2">{analysis.companyRequirements.experience}</p>
              <p className="text-gray-600 text-sm">转行/跨岗：{analysis.companyRequirements.careerChange}</p>
            </div>
            
            <div className="p-4 bg-indigo-50 rounded-xl">
              <h3 className="font-semibold text-gray-800 mb-2">3. 证书/资质</h3>
              <p className="text-gray-700">{analysis.companyRequirements.certificates || '暂无特殊要求'}</p>
            </div>
            
            <div className="p-4 bg-indigo-50 rounded-xl">
              <h3 className="font-semibold text-gray-800 mb-2">4. 隐性偏好</h3>
              <p className="text-gray-700">{analysis.companyRequirements['隐性偏好'] || '大厂背景优先、开源项目经验加分'}</p>
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
                {analysis.gapAnalysis.map((item, idx) => (
                  <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className="border border-gray-300 px-4 py-3 text-sm text-gray-700 font-medium">{item.dimension}</td>
                    <td className="border border-gray-300 px-4 py-3 text-sm text-gray-700">{item.target}</td>
                    <td className="border border-gray-300 px-4 py-3 text-sm text-gray-700">{item.current}</td>
                    <td className={`border border-gray-300 px-4 py-3 text-sm font-medium ${
                      item.gap === '达标' ? 'text-green-600' : 'text-orange-600'
                    }`}>{item.gap}</td>
                    <td className="border border-gray-300 px-4 py-3 text-sm text-gray-700">
                      {item.frequency ? `${item.frequency}次` : '-'}
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

        {analysis.skillRecommendations && analysis.skillRecommendations.length > 0 && (
          <div className="bg-white rounded-3xl p-8 shadow-2xl mb-10">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
              <BookOpen className="w-7 h-7 text-teal-600" />
              技能学习推荐
            </h2>
            <div className="grid md:grid-cols-2 gap-4">
              {analysis.skillRecommendations.map((rec, idx) => (
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
              {analysis.actionPath.shortTerm.map((action, idx) => (
                <div key={idx} className="flex items-start gap-3 p-4 bg-green-50 rounded-xl">
                  <CheckCircle2 className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">{action}</span>
                </div>
              ))}
            </div>
          </div>
          
          <div className="mb-8">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">中期（3-6个月）</h3>
            <div className="space-y-4">
              {analysis.actionPath.midTerm.map((action, idx) => (
                <div key={idx} className="flex items-start gap-3 p-4 bg-blue-50 rounded-xl">
                  <CheckCircle2 className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">{action}</span>
                </div>
              ))}
            </div>
          </div>
          
          <div>
            <h3 className="text-xl font-semibold text-gray-800 mb-4">长期（6-12个月）</h3>
            <div className="space-y-4">
              {analysis.actionPath.longTerm.map((action, idx) => (
                <div key={idx} className="flex items-start gap-3 p-4 bg-purple-50 rounded-xl">
                  <CheckCircle2 className="w-5 h-5 text-purple-500 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">{action}</span>
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
              <p className="text-gray-700">{analysis.competitionAnalysis.supplyDemand}</p>
            </div>
            
            <div className="p-4 bg-red-50 rounded-xl">
              <h3 className="font-semibold text-gray-800 mb-2">2. 竞争者画像</h3>
              <p className="text-gray-700 text-sm">{analysis.competitionAnalysis.competitorProfile}</p>
            </div>
            
            <div className="p-4 bg-red-50 rounded-xl">
              <h3 className="font-semibold text-gray-800 mb-2">3. 你的优势</h3>
              <p className="text-gray-700 text-sm">{analysis.competitionAnalysis.userCompetitiveness.strengths}</p>
            </div>
            
            <div className="p-4 bg-red-50 rounded-xl">
              <h3 className="font-semibold text-gray-800 mb-2">4. 需要提升</h3>
              <p className="text-gray-700 text-sm">{analysis.competitionAnalysis.userCompetitiveness.weaknesses}</p>
            </div>
          </div>
          
          {analysis.competitionAnalysis.marketInsight && (
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
              <div className="text-2xl font-bold text-purple-700 mb-3">{analysis.estimatedTime}</div>
              <div className="text-gray-700 whitespace-pre-line">{analysis.timeReasoning}</div>
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
