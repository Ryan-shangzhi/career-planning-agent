import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Briefcase, Target, TrendingUp, BrainCircuit, Search, Loader2 } from 'lucide-react';
import { api, Job } from '@/services/api';

export default function Home() {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchKeyword, setSearchKeyword] = useState('');
  const [searchCity, setSearchCity] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await api.jobs.getJobs(searchKeyword || undefined, searchCity || undefined);
      setJobs(data);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : '获取职位失败';
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const formatSalary = (min: number | null, max: number | null) => {
    if (!min && !max) return '面议';
    if (!max) return `${(min || 0) / 1000}K+`;
    return `${(min || 0) / 1000}K-${max / 1000}K`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          {/* 英雄区域 */}
          <div className="text-center mb-16 animate-fadeIn">
            <div className="inline-block bg-blue-100 rounded-full px-6 py-3 mb-6">
              <span className="text-blue-800 font-semibold text-sm">
                🎯 智能职业规划顾问
              </span>
            </div>
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
              你好，我是你的
              <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                职业规划顾问
              </span>
            </h1>
            <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto">
              告诉我你的现状和目标，我帮你分析如何一步步实现理想的职业发展
            </p>
            <button
              onClick={() => navigate('/survey')}
              className="inline-flex items-center gap-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-10 py-5 rounded-2xl text-lg font-semibold shadow-xl hover:shadow-2xl transform hover:-translate-y-1 transition-all duration-300"
            >
              <Target className="w-6 h-6" />
              开始规划我的职业
            </button>
          </div>

          {/* 服务特色 */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
            {[
              { icon: Briefcase, title: '岗位查询', desc: '了解目标公司组织架构和岗位设置' },
              { icon: BrainCircuit, title: '竞争分析', desc: '分析岗位竞争情况和入行门槛' },
              { icon: TrendingUp, title: '能力规划', desc: '对比现状差距，制定能力提升计划' },
              { icon: Target, title: '路径设计', desc: '短期、中期、长期清晰的行动指南' },
            ].map((feature, idx) => (
              <div
                key={idx}
                className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transform hover:-translate-y-2 transition-all duration-300"
              >
                <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-xl flex items-center justify-center mb-4">
                  <feature.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{feature.title}</h3>
                <p className="text-gray-600 text-sm">{feature.desc}</p>
              </div>
            ))}
          </div>

          {/* 职位搜索 */}
          <div className="bg-white rounded-3xl p-6 shadow-xl mb-8">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">职位搜索</h3>
            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl text-red-600 text-sm">
                ⚠️ {error}
              </div>
            )}
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="搜索职位关键词..."
                    value={searchKeyword}
                    onChange={(e) => setSearchKeyword(e.target.value)}
                    className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-50 outline-none transition-all"
                  />
                </div>
              </div>
              <input
                type="text"
                placeholder="城市（如：北京）"
                value={searchCity}
                onChange={(e) => setSearchCity(e.target.value)}
                className="md:w-48 px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-50 outline-none transition-all"
              />
              <button
                onClick={fetchJobs}
                disabled={loading}
                className="flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-5 h-5" />}
                搜索
              </button>
            </div>
          </div>

          {/* 职位列表 */}
          {jobs.length > 0 && (
            <div className="bg-white rounded-3xl p-6 shadow-xl mb-8">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">最新职位</h3>
              <div className="space-y-4">
                {jobs.slice(0, 5).map((job) => (
                  <div
                    key={job.id}
                    className="p-4 border border-gray-100 rounded-xl hover:border-blue-200 hover:shadow-md transition-all cursor-pointer"
                  >
                    <div className="flex flex-wrap items-start justify-between gap-4">
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-900 mb-1">{job.title}</h4>
                        <p className="text-gray-500 text-sm mb-2">{job.company_name} · {job.location}</p>
                        <div className="flex flex-wrap gap-2">
                          {job.skills?.split(',').slice(0, 3).map((skill, idx) => (
                            <span
                              key={idx}
                              className="px-2 py-1 bg-blue-50 text-blue-600 text-xs rounded-full"
                            >
                              {skill.trim()}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-blue-600">
                          {formatSalary(job.salary_min, job.salary_max)}
                        </p>
                        <p className="text-gray-500 text-xs">{job.experience_requirement} · {job.education_requirement}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 流程介绍 */}
          <div className="bg-white rounded-3xl p-8 md:p-12 shadow-2xl">
            <h2 className="text-3xl font-bold text-gray-900 text-center mb-10">
              规划流程
            </h2>
            <div className="grid md:grid-cols-4 gap-6">
              {[
                { step: 1, title: '了解现状', desc: '填写你的职业背景和目标' },
                { step: 2, title: '信息收集', desc: '搜索分析行业数据和岗位要求' },
                { step: 3, title: '差距分析', desc: '对比现状与目标的差距' },
                { step: 4, title: '给出建议', desc: '定制化的行动计划' },
              ].map((item, idx) => (
                <div key={idx} className="text-center">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-full flex items-center justify-center mx-auto mb-4 text-white font-bold text-xl">
                    {item.step}
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-2">{item.title}</h3>
                  <p className="text-gray-600 text-sm">{item.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}
