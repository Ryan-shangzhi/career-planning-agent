
import { useNavigate } from 'react-router-dom';
import { Briefcase, Target, TrendingUp, BrainCircuit } from 'lucide-react';

export default function Home() {
  const navigate = useNavigate();

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
      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fadeIn {
          animation: fadeIn 0.8s ease-out;
        }
      `}</style>
    </div>
  );
}

