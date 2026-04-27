
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '@/store';
import { ArrowLeft, RefreshCw, Building2, DollarSign, TrendingUp, AlertCircle, CheckCircle2, Clock, Calendar, Target } from 'lucide-react';

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

        {/* 标题区域 */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            你的职业规划分析报告
          </h1>
          <p className="text-xl text-gray-600">
            目标：{survey.targetCompany} · {survey.targetPosition} · {survey.targetSalary}
          </p>
        </div>

        {/* 信息收集结果 */}
        <div className="grid md:grid-cols-3 gap-6 mb-10">
          <div className="bg-white rounded-2xl p-6 shadow-xl">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-xl flex items-center justify-center">
                <Building2 className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-semibold text-gray-900">组织架构</h3>
            </div>
            <ul className="space-y-2">
              {analysis.companyStructure.map((item, idx) => (
                <li key={idx} className="text-sm text-gray-600 flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  {item}
                </li>
              ))}
            </ul>
          </div>

          <div className="bg-white rounded-2xl p-6 shadow-xl">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-amber-500 rounded-xl flex items-center justify-center">
                <DollarSign className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-semibold text-gray-900">薪资水平</h3>
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

        {/* 岗位要求 */}
        <div className="bg-white rounded-3xl p-8 shadow-2xl mb-10">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <Target className="w-7 h-7 text-blue-600" />
            岗位招聘要求
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

        {/* 一、目标岗位能力图谱 */}
        <div className="bg-white rounded-3xl p-8 shadow-2xl mb-10">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <Target className="w-7 h-7 text-blue-600" />
            一、目标岗位能力图谱
          </h2>
          
          {/* 1. 硬技能清单 */}
          <div className="mb-8">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">1. 硬技能清单（具体到技能名称+熟练程度）</h3>
            <div className="p-4 bg-blue-50 rounded-xl">
              <p className="text-gray-700">
                {analysis.hardSkills.map((skill, idx) => (
                  <span key={idx} className="inline-block mr-4 mb-2">
                    {skill.name}（{skill.level}）{idx < analysis.hardSkills.length - 1 ? '、' : ''}
                  </span>
                ))}
              </p>
            </div>
          </div>
          
          {/* 2. 软技能清单 */}
          <div>
            <h3 className="text-xl font-semibold text-gray-800 mb-4">2. 软技能清单（具体到行为表现）</h3>
            <div className="p-4 bg-green-50 rounded-xl">
              <p className="text-gray-700">
                {analysis.softSkills.map((skill, idx) => (
                  <span key={idx} className="inline-block mr-4 mb-2">
                    {skill.name}（{skill.level}）{idx < analysis.softSkills.length - 1 ? '、' : ''}
                  </span>
                ))}
              </p>
            </div>
          </div>
        </div>

        {/* 二、目标公司/行业人员要求 */}
        <div className="bg-white rounded-3xl p-8 shadow-2xl mb-10">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <Building2 className="w-7 h-7 text-indigo-600" />
            二、目标公司/行业人员要求
          </h2>
          
          <div className="grid md:grid-cols-2 gap-6">
            {/* 1. 学历门槛 */}
            <div className="p-4 bg-indigo-50 rounded-xl">
              <h3 className="font-semibold text-gray-800 mb-2">1. 学历门槛</h3>
              <p className="text-gray-700 mb-2">{analysis.companyRequirements.education}</p>
              <p className="text-gray-600 text-sm">放宽空间：{analysis.companyRequirements.educationFlexibility}</p>
            </div>
            
            {/* 2. 经验要求 */}
            <div className="p-4 bg-indigo-50 rounded-xl">
              <h3 className="font-semibold text-gray-800 mb-2">2. 经验要求</h3>
              <p className="text-gray-700 mb-2">{analysis.companyRequirements.experience}</p>
              <p className="text-gray-600 text-sm">转行/跨岗：{analysis.companyRequirements.careerChange}</p>
            </div>
            
            {/* 3. 证书/资质 */}
            <div className="p-4 bg-indigo-50 rounded-xl">
              <h3 className="font-semibold text-gray-800 mb-2">3. 证书/资质</h3>
              <p className="text-gray-700">{analysis.companyRequirements.certificates}</p>
            </div>
            
            {/* 4. 隐性偏好 */}
            <div className="p-4 bg-indigo-50 rounded-xl">
              <h3 className="font-semibold text-gray-800 mb-2">4. 隐性偏好</h3>
              <p className="text-gray-700">{analysis.companyRequirements['隐性偏好']}</p>
            </div>
          </div>
        </div>

        {/* 三、用户差距分析表 */}
        <div className="bg-white rounded-3xl p-8 shadow-2xl mb-10">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <AlertCircle className="w-7 h-7 text-orange-500" />
            三、用户差距分析表
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="bg-gray-100">
                  <th className="border border-gray-300 px-4 py-3 text-left text-sm font-semibold text-gray-700">维度</th>
                  <th className="border border-gray-300 px-4 py-3 text-left text-sm font-semibold text-gray-700">目标要求</th>
                  <th className="border border-gray-300 px-4 py-3 text-left text-sm font-semibold text-gray-700">用户现状</th>
                  <th className="border border-gray-300 px-4 py-3 text-left text-sm font-semibold text-gray-700">差距程度</th>
                  <th className="border border-gray-300 px-4 py-3 text-left text-sm font-semibold text-gray-700">补足难度</th>
                </tr>
              </thead>
              <tbody>
                {analysis.gapAnalysis.map((item, idx) => (
                  <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className="border border-gray-300 px-4 py-3 text-sm text-gray-700">{item.dimension}</td>
                    <td className="border border-gray-300 px-4 py-3 text-sm text-gray-700">{item.target}</td>
                    <td className="border border-gray-300 px-4 py-3 text-sm text-gray-700">{item.current}</td>
                    <td className={`border border-gray-300 px-4 py-3 text-sm font-medium ${
                      item.gap === '小' ? 'text-green-600' : item.gap === '中' ? 'text-yellow-600' : 'text-orange-600'
                    }`}>{item.gap}</td>
                    <td className="border border-gray-300 px-4 py-3 text-sm text-gray-700">{item.difficulty}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* 四、行动路径 */}
        <div className="bg-white rounded-3xl p-8 shadow-2xl mb-10">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <CheckCircle2 className="w-7 h-7 text-green-600" />
            四、行动路径（必须具体）
          </h2>
          
          {/* 短期（1-3个月） */}
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
          
          {/* 中期（3-6个月） */}
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
          
          {/* 长期（6-12个月） */}
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

        {/* 五、竞争力度分析 */}
        <div className="bg-white rounded-3xl p-8 shadow-2xl mb-10">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <TrendingUp className="w-7 h-7 text-red-600" />
            五、竞争力度分析
          </h2>
          
          <div className="grid md:grid-cols-3 gap-6">
            {/* 1. 该岗位供需情况 */}
            <div className="p-4 bg-red-50 rounded-xl">
              <h3 className="font-semibold text-gray-800 mb-2">1. 该岗位供需情况</h3>
              <p className="text-gray-700">{analysis.competitionAnalysis.supplyDemand}</p>
            </div>
            
            {/* 2. 竞争者画像 */}
            <div className="p-4 bg-red-50 rounded-xl">
              <h3 className="font-semibold text-gray-800 mb-2">2. 竞争者画像</h3>
              <p className="text-gray-700 text-sm">{analysis.competitionAnalysis.competitorProfile}</p>
            </div>
            
            {/* 3. 用户竞争力评估 */}
            <div className="p-4 bg-red-50 rounded-xl">
              <h3 className="font-semibold text-gray-800 mb-2">3. 用户竞争力评估</h3>
              <p className="text-gray-700 text-sm mb-2">优势：{analysis.competitionAnalysis.userCompetitiveness.strengths}</p>
              <p className="text-gray-700 text-sm">劣势：{analysis.competitionAnalysis.userCompetitiveness.weaknesses}</p>
            </div>
          </div>
        </div>

        {/* 六、晋升路径预览 */}
        <div className="bg-white rounded-3xl p-8 shadow-2xl mb-10">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <Target className="w-7 h-7 text-purple-600" />
            六、晋升路径预览
          </h2>
          
          <div className="space-y-4">
            {analysis.promotionPath.map((path, idx) => (
              <div key={idx} className="p-5 bg-purple-50 rounded-2xl">
                <p className="text-gray-700 text-center">{path}</p>
              </div>
            ))}
          </div>
        </div>

        {/* 达成时间评估 */}
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



        {/* 底部按钮 */}
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

