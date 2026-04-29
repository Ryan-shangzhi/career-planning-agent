
import { UserSurvey, AnalysisResult } from '@/store';

export function generateAnalysis(survey: UserSurvey): AnalysisResult {
  // 模拟岗位信息调研（实际应用中应使用真实搜索）
  const positionLower = survey.targetPosition.toLowerCase();
  const companyLower = survey.targetCompany.toLowerCase();
  const experienceYears = survey.experienceYears;
  const skills = survey.skills.toLowerCase();
  
  // 步骤一：岗位信息调研
  // 模拟搜索结果，实际应用中应调用搜索API
  const positionResearch = {
    responsibilities: getPositionResponsibilities(survey.targetPosition),
    requiredSkills: getRequiredSkills(survey.targetPosition),
    companyRequirements: survey.targetCompany ? getCompanySpecificRequirements(survey.targetCompany, survey.targetPosition) : [],
    promotionPath: getPromotionPath(survey.targetPosition)
  };
  
  // 步骤二：行业特征识别
  const industryType = identifyIndustryType(survey.targetPosition);
  
  // 步骤三：用户现状校准
  const calibratedSkills = calibrateUserSkills(skills, experienceYears);
  
  // 根据目标公司调整组织架构
  let companyStructure = [];
  if (companyLower.includes('阿里') || companyLower.includes('alibaba')) {
    companyStructure = [
      '淘天集团 - 淘宝/天猫',
      '阿里云智能 - 云计算',
      '国际数字商业 - 跨境电商',
      '本地生活 - 饿了么/高德',
      '云智能 - 技术研发',
    ];
  } else if (companyLower.includes('腾讯') || companyLower.includes('tencent')) {
    companyStructure = [
      '腾讯视频 - 内容生态',
      '腾讯云 - 云计算',
      '游戏业务 - 腾讯游戏',
      '社交网络 - 微信/QQ',
      '金融科技 - 微信支付',
    ];
  } else if (companyLower.includes('字节') || companyLower.includes('bytedance')) {
    companyStructure = [
      '抖音 - 短视频',
      '飞书 - 企业协作',
      '电商 - 抖音电商',
      '国际化 - TikTok',
      '技术中台 - 算法/工程',
    ];
  } else if (companyLower.includes('百度') || companyLower.includes('baidu')) {
    companyStructure = [
      '搜索业务 - 百度搜索',
      '智能云 - 百度云',
      'AI 业务 - 文心一言',
      '自动驾驶 - 百度Apollo',
      '移动生态 - 百度App',
    ];
  } else if (companyLower.includes('京东') || companyLower.includes('jd')) {
    companyStructure = [
      '零售业务 - 京东商城',
      '物流业务 - 京东物流',
      '科技业务 - 京东科技',
      '健康业务 - 京东健康',
      '产发业务 - 京东产发',
    ];
  } else if (companyLower.includes('美团') || companyLower.includes('meituan')) {
    companyStructure = [
      '外卖业务 - 美团外卖',
      '到店酒旅 - 美团到店',
      '出行业务 - 美团打车',
      '闪购业务 - 美团闪购',
      '优选业务 - 美团优选',
    ];
  } else if (companyLower.includes('华为') || companyLower.includes('huawei')) {
    companyStructure = [
      '消费者业务 - 手机/平板',
      '运营商业务 - 通信设备',
      '企业业务 - 企业解决方案',
      '云业务 - 华为云',
      '智能汽车 - 华为智选',
    ];
  } else if (companyLower.includes('小米') || companyLower.includes('xiaomi')) {
    companyStructure = [
      '手机业务 - 小米手机',
      '生态链 - 小米生态',
      'IoT业务 - 智能家居',
      '互联网服务 - MIUI',
      '海外业务 - 国际化',
    ];
  } else if (companyLower.includes('网易') || companyLower.includes('netease')) {
    companyStructure = [
      '游戏业务 - 网易游戏',
      '邮箱业务 - 网易邮箱',
      '音乐业务 - 网易云音乐',
      '电商业务 - 网易严选',
      '教育业务 - 网易有道',
    ];
  } else if (companyLower.includes('拼多多') || companyLower.includes('pdd')) {
    companyStructure = [
      '电商业务 - 拼多多',
      '跨境电商 - Temu',
      '社区团购 - 多多买菜',
      '技术平台 - 算法/工程',
      '用户增长 - 营销推广',
    ];
  } else {
    // 根据公司类型生成通用组织架构
    if (companyLower.includes('科技') || companyLower.includes('tech') || companyLower.includes('互联网')) {
      companyStructure = [
        '研发部 - 产品研发团队',
        '技术部 - 前端/后端开发',
        '产品部 - 产品设计团队',
        '运营部 - 用户增长团队',
        '市场部 - 品牌营销',
      ];
    } else if (companyLower.includes('金融') || companyLower.includes('银行') || companyLower.includes('finance')) {
      companyStructure = [
        '风控部 - 风险管理',
        '产品部 - 金融产品',
        '技术部 - 金融科技',
        '市场部 - 客户营销',
        '运营部 - 客户服务',
      ];
    } else if (companyLower.includes('教育') || companyLower.includes('education')) {
      companyStructure = [
        '教研部 - 课程研发',
        '教学部 - 教师团队',
        '技术部 - 教育科技',
        '市场部 - 招生营销',
        '运营部 - 学生服务',
      ];
    } else if (companyLower.includes('电商') || companyLower.includes('ecommerce')) {
      companyStructure = [
        '商品部 - 选品采购',
        '技术部 - 电商平台',
        '运营部 - 活动运营',
        '市场部 - 流量获取',
        '客服部 - 客户服务',
      ];
    } else if (companyLower.includes('游戏') || companyLower.includes('game')) {
      companyStructure = [
        '研发部 - 游戏开发',
        '美术部 - 游戏美术',
        '策划部 - 游戏策划',
        '运营部 - 游戏运营',
        '市场部 - 游戏发行',
      ];
    } else {
      // 通用组织架构
      companyStructure = [
        '技术部 - 产品研发团队',
        '产品部 - 产品设计团队',
        '运营部 - 用户增长团队',
        '市场部 - 品牌营销',
        '行政部 - 综合管理',
      ];
    }
  }
  
  let requirements = [
    '3年以上相关工作经验',
    '熟练掌握核心技术栈',
    '具备良好的团队协作能力',
    '有成功项目经验者优先',
    '优秀的问题分析和解决能力',
  ];
  
  let salaryRange = '20K - 40K';
  let competition = '竞争激烈，岗位供需比约为 1:15';
  let difficulty = '中等难度，预计需要 1-2 年积累';
  
  // 根据不同岗位类型调整内容
  if (positionLower.includes('前端') || positionLower.includes('web')) {
    requirements = [
      '精通 HTML、CSS、JavaScript/TypeScript',
      '熟练使用 React/Vue/Angular 等主流框架',
      '了解前端工程化、性能优化',
      '有响应式设计和移动端适配经验',
      '熟悉 Node.js 和常用构建工具',
    ];
    salaryRange = '18K - 35K';
    competition = '竞争较为激烈，岗位供需比约为 1:12';
  } else if (positionLower.includes('后端')) {
    requirements = [
      '精通 Java/Python/Go 等至少一门后端语言',
      '熟悉 Spring/Django/Flask 等主流框架',
      '掌握 MySQL/PostgreSQL/MongoDB 等数据库',
      '了解微服务架构和分布式系统',
      '有高并发、高性能系统开发经验优先',
    ];
    salaryRange = '22K - 45K';
    competition = '竞争适中，岗位供需比约为 1:8';
  } else if (positionLower.includes('产品')) {
    requirements = [
      '3年以上互联网产品经验',
      '优秀的逻辑分析和用户思维',
      '熟练使用 Axure、Figma 等工具',
      '具备数据驱动的产品决策能力',
      '有成功产品上线经验优先',
    ];
    salaryRange = '20K - 40K';
    competition = '竞争激烈，岗位供需比约为 1:20';
    difficulty = '较高难度，需要全面的能力积累';
  } else if (positionLower.includes('运营')) {
    requirements = [
      '2年以上互联网运营经验',
      '熟悉内容运营、用户运营、活动运营',
      '具备数据分析能力',
      '优秀的文案写作和沟通能力',
      '有用户增长成功案例优先',
    ];
    salaryRange = '15K - 30K';
    competition = '竞争适中，岗位供需比约为 1:10';
  }
  
  // 生成目标岗位能力图谱
  const hardSkills = [];
  const softSkills = [];
  
  // 使用岗位调研结果生成技能清单
  const requiredSkills = positionResearch.requiredSkills;
  
  // 根据具体岗位生成详细技能清单
  // 复用之前声明的 positionLower 变量
  
  if (positionLower.includes('前端')) {
    // 前端工程师
    hardSkills.push(
      { name: 'JavaScript', level: '精通', application: '前端核心编程语言' },
      { name: 'TypeScript', level: '熟练', application: '类型安全的JavaScript超集' },
      { name: 'Vue.js 或 React', level: '精通', application: '前端框架开发' },
      { name: 'Vue-Router/React-Router', level: '熟练', application: '前端路由管理' },
      { name: 'Vuex/Redux', level: '熟练', application: '前端状态管理' },
      { name: 'Webpack/Vite', level: '熟练', application: '前端构建工具' },
      { name: 'HTML5/CSS3', level: '精通', application: '网页结构和样式' },
      { name: 'Git', level: '熟练', application: '版本控制' }
    );
    softSkills.push(
      { name: '问题解决', level: '能独立解决技术难题', importance: '前端开发中经常遇到兼容性和性能问题' },
      { name: '团队协作', level: '能与产品、设计、后端团队有效协作', importance: '前端需要与多个团队配合' },
      { name: '学习能力', level: '快速掌握新技术', importance: '前端技术更新迭代快' }
    );
  } else if (positionLower.includes('后端') && (positionLower.includes('java') || positionLower.includes('Java'))) {
    // 后端工程师（Java方向）
    hardSkills.push(
      { name: 'Java', level: '精通', application: '后端核心编程语言' },
      { name: 'Spring Boot', level: '熟练', application: 'Java应用开发框架' },
      { name: 'Spring Cloud', level: '熟练', application: '微服务架构框架' },
      { name: 'MyBatis', level: '熟练', application: 'ORM框架' },
      { name: 'MySQL', level: '精通', application: '关系型数据库' },
      { name: 'Redis', level: '熟练', application: '缓存系统' },
      { name: 'Maven', level: '熟练', application: '项目构建工具' },
      { name: 'Git', level: '熟练', application: '版本控制' }
    );
    softSkills.push(
      { name: '系统设计', level: '能设计高并发系统', importance: '后端需要考虑系统的可扩展性和性能' },
      { name: '问题排查', level: '能快速定位和解决生产问题', importance: '后端系统出现问题时需要及时排查' },
      { name: '团队协作', level: '能与前端、产品等团队有效协作', importance: '后端开发需要与多个团队配合' }
    );
  } else if (positionLower.includes('后端') && (positionLower.includes('python') || positionLower.includes('Python'))) {
    // 后端工程师（Python方向）
    hardSkills.push(
      { name: 'Python', level: '精通', application: '后端核心编程语言' },
      { name: 'Django 或 Flask', level: '熟练', application: 'Python Web框架' },
      { name: 'FastAPI', level: '熟练', application: '高性能API框架' },
      { name: 'MySQL', level: '熟练', application: '关系型数据库' },
      { name: 'PostgreSQL', level: '熟练', application: '开源关系型数据库' },
      { name: 'Redis', level: '熟练', application: '缓存系统' },
      { name: 'Git', level: '熟练', application: '版本控制' }
    );
    softSkills.push(
      { name: '问题解决', level: '能独立解决技术难题', importance: '后端开发中经常遇到各种技术问题' },
      { name: '团队协作', level: '能与前端、产品等团队有效协作', importance: '后端开发需要与多个团队配合' },
      { name: '学习能力', level: '快速掌握新技术', importance: 'Python生态系统不断发展' }
    );
  } else if (positionLower.includes('数据') && positionLower.includes('分析')) {
    // 数据分析师
    hardSkills.push(
      { name: 'Python', level: '熟练', application: '数据处理和分析' },
      { name: 'SQL', level: '精通', application: '数据库查询和分析' },
      { name: 'Excel', level: '精通', application: '数据处理和可视化' },
      { name: 'Tableau/PowerBI', level: '熟练', application: '数据可视化工具' },
      { name: 'Pandas', level: '熟练', application: 'Python数据分析库' },
      { name: 'NumPy', level: '熟练', application: 'Python数值计算库' },
      { name: 'Matplotlib', level: '熟练', application: 'Python数据可视化库' }
    );
    softSkills.push(
      { name: '数据分析思维', level: '能从数据中提取有价值的信息', importance: '数据分析师的核心能力' },
      { name: '沟通表达', level: '能清晰表达分析结果', importance: '需要向非技术人员解释分析结果' },
      { name: '问题解决', level: '能通过数据分析解决业务问题', importance: '数据分析的最终目的是解决问题' }
    );
  } else if (positionLower.includes('测试')) {
    // 测试工程师
    hardSkills.push(
      { name: 'Python 或 Java', level: '熟练', application: '自动化测试脚本开发' },
      { name: 'Selenium', level: '熟练', application: 'Web自动化测试' },
      { name: 'JMeter', level: '熟练', application: '性能测试' },
      { name: 'Postman', level: '熟练', application: 'API测试' },
      { name: 'Pytest 或 JUnit', level: '熟练', application: '单元测试框架' }
    );
    softSkills.push(
      { name: '细心', level: '能发现细微的问题', importance: '测试需要细致入微' },
      { name: '沟通能力', level: '能清晰表达测试结果和问题', importance: '需要与开发团队沟通问题' },
      { name: '问题分析', level: '能分析问题的根本原因', importance: '测试不仅要发现问题，还要分析原因' }
    );
  } else if (positionLower.includes('运维')) {
    // 运维工程师
    hardSkills.push(
      { name: 'Shell脚本', level: '精通', application: '系统自动化操作' },
      { name: 'Python', level: '熟练', application: '运维自动化脚本' },
      { name: 'Docker', level: '熟练', application: '容器化部署' },
      { name: 'Kubernetes', level: '熟练', application: '容器编排' },
      { name: 'Linux', level: '精通', application: '系统管理' },
      { name: 'Jenkins', level: '熟练', application: 'CI/CD工具' },
      { name: 'Nginx', level: '熟练', application: 'Web服务器' }
    );
    softSkills.push(
      { name: '问题排查', level: '能快速定位和解决系统问题', importance: '运维需要及时解决系统故障' },
      { name: '抗压能力', level: '能在系统故障时保持冷静', importance: '运维工作经常面临紧急情况' },
      { name: '学习能力', level: '快速掌握新的运维工具和技术', importance: '运维技术不断发展' }
    );
  } else if (positionLower.includes('ui') || (positionLower.includes('设计') && positionLower.includes('界面'))) {
    // UI设计师
    hardSkills.push(
      { name: 'Figma', level: '精通', application: 'UI设计工具' },
      { name: 'Photoshop', level: '精通', application: '图像处理' },
      { name: 'Sketch', level: '熟练', application: 'UI设计工具' },
      { name: 'Adobe XD', level: '熟练', application: 'UI/UX设计工具' },
      { name: 'Illustrator', level: '熟练', application: '矢量图形设计' }
    );
    softSkills.push(
      { name: '创意思维', level: '能提出创新设计方案', importance: 'UI设计需要不断创新' },
      { name: '审美能力', level: '具备良好的美学素养', importance: 'UI设计需要符合美学标准' },
      { name: '沟通表达', level: '能清晰表达设计理念', importance: '需要与产品、开发团队沟通设计方案' }
    );
  } else if (positionLower.includes('产品')) {
    // 产品经理
    hardSkills.push(
      { name: 'Axure', level: '熟练', application: '产品原型设计' },
      { name: 'Figma', level: '熟练', application: '产品设计工具' },
      { name: 'XMind', level: '熟练', application: '思维导图工具' },
      { name: 'Excel', level: '熟练', application: '数据处理和分析' },
      { name: 'SQL', level: '基础', application: '数据查询' }
    );
    softSkills.push(
      { name: '需求分析', level: '能准确理解和拆解用户需求', importance: '产品经理的核心能力' },
      { name: '沟通协调', level: '能协调多个部门资源', importance: '产品需要与技术、设计、运营等部门合作' },
      { name: '决策能力', level: '能在信息不全的情况下做出合理决策', importance: '产品开发过程中需要频繁做出决策' }
    );
  } else if (positionLower.includes('运营')) {
    // 运营专员
    hardSkills.push(
      { name: '秀米/135编辑器', level: '熟练', application: '内容编辑' },
      { name: 'Canva', level: '熟练', application: '简单设计' },
      { name: '剪映', level: '熟练', application: '视频剪辑' },
      { name: 'Excel', level: '熟练', application: '数据处理和分析' },
      { name: '小红书', level: '熟练', application: '内容平台运营' },
      { name: '抖音', level: '熟练', application: '短视频平台运营' }
    );
    softSkills.push(
      { name: '文案写作', level: '能撰写吸引人的文案', importance: '运营需要通过文案吸引用户' },
      { name: '创意能力', level: '能提出创新运营方案', importance: '运营需要不断创新以吸引用户' },
      { name: '沟通协调', level: '能与产品、技术等部门配合', importance: '运营需要推动产品功能的落地和优化' }
    );
  } else if (positionLower.includes('行政')) {
    // 行政前台
    hardSkills.push(
      { name: 'Excel', level: '熟练', application: '数据处理和报表' },
      { name: 'PPT', level: '熟练', application: '演示文稿制作' },
      { name: 'Word', level: '熟练', application: '文档编辑' },
      { name: 'OA系统', level: '熟练', application: '办公自动化系统' },
      { name: '钉钉/企业微信', level: '熟练', application: '企业通讯和管理' }
    );
    softSkills.push(
      { name: '沟通表达', level: '能清晰表达和协调事务', importance: '行政需要与各部门沟通协调' },
      { name: '细心', level: '能注意细节', importance: '行政工作需要处理很多细节' },
      { name: '服务意识', level: '具备良好的服务态度', importance: '行政工作本质是服务' }
    );
  } else if (positionLower.includes('hr') || positionLower.includes('人事')) {
    // HR专员
    hardSkills.push(
      { name: 'Excel', level: '熟练', application: '数据处理和报表' },
      { name: 'PPT', level: '熟练', application: '演示文稿制作' },
      { name: 'ATS招聘系统', level: '熟练', application: '招聘管理系统' },
      { name: 'HR系统', level: '熟练', application: '人力资源管理系统' }
    );
    softSkills.push(
      { name: '沟通表达', level: '能与候选人有效沟通', importance: 'HR需要与候选人进行面试和沟通' },
      { name: '识人能力', level: '能准确评估候选人', importance: 'HR需要招聘合适的人才' },
      { name: '保密意识', level: '能保守公司和员工信息', importance: 'HR需要处理很多敏感信息' }
    );
  } else if (positionLower.includes('会计') || positionLower.includes('财务')) {
    // 会计
    hardSkills.push(
      { name: '金蝶/用友', level: '熟练', application: '财务软件' },
      { name: 'Excel', level: '精通', application: '财务数据处理和分析' },
      { name: 'PPT', level: '熟练', application: '财务报告演示' },
      { name: 'SAP', level: '基础', application: '企业资源规划系统' }
    );
    softSkills.push(
      { name: '细心', level: '能处理复杂的财务数据', importance: '会计工作需要高度准确性' },
      { name: '保密意识', level: '能保守公司财务信息', importance: '财务信息是公司的核心机密' },
      { name: '责任心', level: '对工作高度负责', importance: '财务工作关系到公司的经济利益' }
    );
  } else if (industryType === '设计类') {
    // 其他设计类岗位
    hardSkills.push(
      { name: 'UI/UX设计', level: '熟练', application: '产品界面设计和用户体验优化' },
      { name: 'Figma/Sketch/Adobe XD', level: '精通', application: '设计工具使用' },
      { name: '视觉设计', level: '掌握', application: '色彩、排版、构图等视觉元素设计' },
      { name: '交互设计', level: '熟练', application: '用户交互流程设计' }
    );
    softSkills.push(
      { name: '创意思维', level: '能提出创新设计方案', importance: '设计类岗位需要不断创新' },
      { name: '审美能力', level: '具备良好的美学素养', importance: '设计作品需要符合美学标准' },
      { name: '沟通表达', level: '能清晰表达设计理念', importance: '需要与团队成员和客户沟通设计方案' }
    );
  } else if (industryType === '技术类') {
    // 其他技术类岗位
    hardSkills.push(
      { name: requiredSkills[0] || '编程语言', level: '精通', application: '核心技术实现' },
      { name: requiredSkills[1] || '开发框架', level: '熟练', application: '快速开发和构建' },
      { name: requiredSkills[2] || '数据库', level: '掌握', application: '数据存储和管理' },
      { name: requiredSkills[3] || '系统架构', level: '了解', application: '系统设计和优化' }
    );
    softSkills.push(
      { name: '问题解决', level: '能独立解决技术难题', importance: '技术类岗位需要解决各种技术问题' },
      { name: '团队协作', level: '能与其他开发者有效协作', importance: '软件开发通常是团队工作' },
      { name: '学习能力', level: '快速掌握新技术', importance: '技术发展迅速，需要持续学习' }
    );
  } else if (industryType === '运营类') {
    // 其他运营类岗位
    hardSkills.push(
      { name: '数据分析', level: '熟练', application: '分析用户行为和运营效果' },
      { name: '文案写作', level: '熟练', application: '撰写营销文案和活动策划' },
      { name: '活动策划', level: '掌握', application: '设计和执行运营活动' },
      { name: '用户增长', level: '了解', application: '制定用户增长策略' }
    );
    softSkills.push(
      { name: '沟通协调', level: '能与多个部门协作', importance: '运营需要与产品、技术等部门配合' },
      { name: '创意能力', level: '能提出创新运营方案', importance: '运营需要不断创新以吸引用户' },
      { name: '抗压能力', level: '能在压力下完成任务', importance: '运营工作经常面临指标压力' }
    );
  } else if (industryType === '管理类') {
    // 管理类岗位
    hardSkills.push(
      { name: '项目管理', level: '熟练', application: '项目规划和执行' },
      { name: '风险管理', level: '掌握', application: '识别和应对项目风险' },
      { name: '资源管理', level: '了解', application: '合理分配和利用资源' },
      { name: '数据驱动决策', level: '掌握', application: '基于数据做出管理决策' }
    );
    softSkills.push(
      { name: '领导力', level: '能带领团队达成目标', importance: '管理类岗位需要领导团队' },
      { name: '沟通能力', level: '能清晰表达管理意图', importance: '需要与团队成员和上级沟通' },
      { name: '决策能力', level: '能在复杂情况下做出决策', importance: '管理岗位需要频繁做出决策' }
    );
  } else {
    // 其他岗位
    hardSkills.push(
      { name: '专业技能', level: '熟练', application: '完成岗位核心工作' },
      { name: '工具使用', level: '掌握', application: '提高工作效率' },
      { name: '行业知识', level: '了解', application: '理解行业趋势和业务逻辑' }
    );
    softSkills.push(
      { name: '沟通能力', level: '良好', importance: '与团队成员和 stakeholders 有效沟通' },
      { name: '学习能力', level: '较强', importance: '适应行业变化和新技术' },
      { name: '问题解决', level: '基本', importance: '解决工作中遇到的问题' }
    );
  }
  
  // 生成目标公司/行业人员要求
  const companyRequirements = {
    education: industryType === '设计类' ? '本科及以上学历，设计相关专业优先' : 
              industryType === '技术类' ? '本科及以上学历，计算机相关专业优先' : 
              industryType === '运营类' ? '本科及以上学历，市场营销、商务等相关专业优先' : 
              industryType === '管理类' ? '本科及以上学历，管理相关专业优先' : 
              '本科及以上学历，相关专业优先',
    educationFlexibility: '有相关工作经验者可放宽至大专',
    experience: positionLower.includes('初级') ? '1-2年相关经验' : positionLower.includes('高级') ? '3-5年相关经验' : '2-3年相关经验',
    careerChange: '接受转行，需相关技能或项目经验',
    certificates: industryType === '设计类' ? 'Adobe认证、UI设计认证等优先' : 
                 industryType === '技术类' ? 'AWS、Azure等云服务认证、相关技术认证优先' : 
                 industryType === '运营类' ? 'Google数字营销认证、内容营销认证等优先' : 
                 industryType === '管理类' ? 'PMP、ACP等项目管理证书优先' : 
                 '相关行业认证优先',
   隐性偏好: companyLower.includes('阿里') ? '偏好有大型电商项目经验的候选人' : 
             companyLower.includes('腾讯') ? '偏好有社交产品或游戏经验的候选人' : 
             companyLower.includes('字节') ? '偏好有短视频或内容平台经验的候选人' : 
             companyLower.includes('百度') ? '偏好有搜索引擎或AI相关经验的候选人' : 
             companyLower.includes('京东') ? '偏好有电商或物流相关经验的候选人' : 
             companyLower.includes('美团') ? '偏好有本地生活服务相关经验的候选人' : 
             '偏好有相关行业经验和项目成果的候选人'
  };
  
  // 生成用户差距分析表
  const gapAnalysis = [];
  hardSkills.forEach(skill => {
    // 根据工作经验校准用户技能水平
    let currentLevel = '了解基础';
    if (experienceYears >= 10) {
      currentLevel = '精通';
    } else if (experienceYears >= 5) {
      currentLevel = '熟练';
    } else if (experienceYears >= 2) {
      currentLevel = '掌握';
    }
    
    // 根据用户实际技能调整
    if (skills.includes(skill.name.toLowerCase())) {
      currentLevel = experienceYears >= 5 ? '精通' : '熟练';
    }
    
    // 计算差距程度
    let gapLevel = '小';
    let difficulty = '1-3个月';
    
    if (skill.level === '精通') {
      if (currentLevel === '了解基础') {
        gapLevel = '大';
        difficulty = '6-12个月';
      } else if (currentLevel === '掌握') {
        gapLevel = '中';
        difficulty = '3-6个月';
      }
    } else if (skill.level === '熟练') {
      if (currentLevel === '了解基础') {
        gapLevel = '大';
        difficulty = '3-6个月';
      } else if (currentLevel === '掌握') {
        gapLevel = '小';
        difficulty = '1-3个月';
      }
    } else if (skill.level === '掌握') {
      if (currentLevel === '了解基础') {
        gapLevel = '中';
        difficulty = '2-4个月';
      }
    }
    
    gapAnalysis.push({ dimension: `硬技能-${skill.name}`, target: skill.level, current: currentLevel, gap: gapLevel, difficulty });
  });
  
  softSkills.forEach(skill => {
    // 根据工作经验校准用户技能水平
    let currentLevel = '需要提升';
    if (experienceYears >= 10) {
      currentLevel = '优秀';
    } else if (experienceYears >= 5) {
      currentLevel = '良好';
    } else if (experienceYears >= 2) {
      currentLevel = '具备';
    }
    
    // 根据用户实际技能调整
    if (skills.includes(skill.name.toLowerCase())) {
      currentLevel = experienceYears >= 5 ? '优秀' : '良好';
    }
    
    // 计算差距程度
    let gapLevel = '小';
    let difficulty = '1-3个月';
    
    if (skill.level.includes('能独立')) {
      if (currentLevel === '需要提升') {
        gapLevel = '大';
        difficulty = '3-6个月';
      } else if (currentLevel === '具备') {
        gapLevel = '中';
        difficulty = '2-4个月';
      }
    } else if (skill.level === '良好') {
      if (currentLevel === '需要提升') {
        gapLevel = '中';
        difficulty = '2-4个月';
      }
    }
    
    gapAnalysis.push({ dimension: `软技能-${skill.name}`, target: skill.level, current: currentLevel, gap: gapLevel, difficulty });
  });
  
  // 生成具体行动路径
  const actionPath = {
    shortTerm: [],
    midTerm: [],
    longTerm: []
  };
  
  // 根据岗位类型生成行动路径
  switch (industryType) {
    case '行政类':
      // 短期（1-3个月）
      actionPath.shortTerm.push('学习 Excel 高级函数，推荐 Excel Home 教程，每天 1 小时，1 个月完成');
      actionPath.shortTerm.push('学习 PPT 制作技巧，推荐秋叶PPT教程，每天 1 小时，1 个月完成');
      actionPath.shortTerm.push('学习 OA 系统操作，熟悉企业常用办公系统');
      actionPath.shortTerm.push('准备人力资源管理师证或行政管理师证考试');
      
      // 中期（3-6个月）
      actionPath.midTerm.push('积累大厂行政实习或外包经验');
      actionPath.midTerm.push('学习钉钉/企业微信后台管理，熟悉考勤薪酬系统');
      actionPath.midTerm.push('提升会议组织、公文写作、档案管理等核心技能');
      actionPath.midTerm.push('学习供应商管理和固定资产管理');
      
      // 长期（6-12个月）
      actionPath.longTerm.push('准备面试话术，重点突出大厂行政流程和多部门协调经验');
      actionPath.longTerm.push('制定投递策略：先投中小厂积累面试经验，再投目标公司');
      actionPath.longTerm.push('整理行政工作案例，突出问题解决能力');
      break;
      
    case '技术类':
      // 短期（1-3个月）
      actionPath.shortTerm.push('学习编程语言基础，推荐官方文档或权威教程，每天 1.5 小时，2 个月完成');
      actionPath.shortTerm.push('刷 LeetCode 题目，每天 2 道，持续 3 个月');
      actionPath.shortTerm.push('学习相关框架和工具，掌握核心概念');
      
      // 中期（3-6个月）
      actionPath.midTerm.push('完成 2 个完整项目，上传到 GitHub');
      actionPath.midTerm.push('参与开源项目，贡献代码，积累协作经验');
      actionPath.midTerm.push('深入学习系统设计和架构知识');
      
      // 长期（6-12个月）
      actionPath.longTerm.push('准备技术面试题，重点复习算法和系统设计');
      actionPath.longTerm.push('整理项目作品集，突出技术难点和解决方案');
      actionPath.longTerm.push('关注行业动态，学习新技术和趋势');
      break;
      
    case '设计类':
      // 短期（1-3个月）
      actionPath.shortTerm.push('学习设计软件（PS/AI/3DMax等），推荐软件官方教程，每天 2 小时，2 个月完成');
      actionPath.shortTerm.push('临摹优秀作品，每天 1 张，持续 3 个月');
      actionPath.shortTerm.push('学习设计理论和色彩搭配知识');
      
      // 中期（3-6个月）
      actionPath.midTerm.push('制作完整作品集，包含 5-10 个项目');
      actionPath.midTerm.push('参加设计比赛，积累获奖经验');
      actionPath.midTerm.push('学习用户体验设计和交互设计原则');
      
      // 长期（6-12个月）
      actionPath.longTerm.push('优化作品集，突出个人风格和设计思路');
      actionPath.longTerm.push('投递作品集到设计平台（站酷/Behance），增加曝光度');
      actionPath.longTerm.push('建立个人设计品牌，积累行业人脉');
      break;
      
    case '运营类':
      // 短期（1-3个月）
      actionPath.shortTerm.push('学习数据分析基础，推荐《深入浅出数据分析》，每天 1 小时，1 个月完成');
      actionPath.shortTerm.push('学习文案写作技巧，推荐《文案训练手册》，每天 30 分钟，1 个月完成');
      actionPath.shortTerm.push('学习用户增长方法，推荐《增长黑客》，每天 1 小时，1 个月完成');
      actionPath.shortTerm.push('运营一个自己的账号（小红书/抖音），积累实操经验');
      
      // 中期（3-6个月）
      actionPath.midTerm.push('分析 10 个成功运营案例，总结经验和方法');
      actionPath.midTerm.push('积累运营数据，包括粉丝量、转化率等关键指标');
      actionPath.midTerm.push('学习活动策划和执行，提升活动运营能力');
      
      // 长期（6-12个月）
      actionPath.longTerm.push('整理运营案例作品集，突出数据成果');
      actionPath.longTerm.push('准备面试，重点展示运营数据和成功案例');
      actionPath.longTerm.push('建立运营人脉，参与行业活动和社群');
      break;
      
    case 'HR类':
      // 短期（1-3个月）
      actionPath.shortTerm.push('学习招聘流程和技巧，推荐《招聘实战手册》，每天 1 小时，1 个月完成');
      actionPath.shortTerm.push('学习薪酬体系设计和劳动法基础知识');
      actionPath.shortTerm.push('准备人力资源管理师考试');
      
      // 中期（3-6个月）
      actionPath.midTerm.push('积累招聘实战经验，参与完整招聘流程');
      actionPath.midTerm.push('学习 ATS 系统操作和人才盘点方法');
      actionPath.midTerm.push('提升面试技巧和候选人评估能力');
      
      // 长期（6-12个月）
      actionPath.longTerm.push('整理招聘成果数据，突出招聘效率和质量');
      actionPath.longTerm.push('准备面试：招聘案例分析和HR专业知识');
      actionPath.longTerm.push('建立行业人脉，拓展招聘渠道');
      break;
      
    case '财务类':
      // 短期（1-3个月）
      actionPath.shortTerm.push('学习财务软件操作（如用友、金蝶），每天 1 小时，1 个月完成');
      actionPath.shortTerm.push('学习税务知识，了解最新税收政策');
      actionPath.shortTerm.push('准备初级会计证考试，或开始CPA备考');
      
      // 中期（3-6个月）
      actionPath.midTerm.push('积累财务实操经验，参与完整财务流程');
      actionPath.midTerm.push('学习财务报表分析和预算管理');
      actionPath.midTerm.push('提升Excel财务函数和数据处理能力');
      
      // 长期（6-12个月）
      actionPath.longTerm.push('准备面试：财务案例分析和专业知识');
      actionPath.longTerm.push('整理财务工作成果，突出成本控制和财务优化案例');
      actionPath.longTerm.push('关注行业动态，学习财务管理新方法');
      break;
      
    default:
      // 通用行动路径
      // 短期（1-3个月）
      actionPath.shortTerm.push('学习目标岗位所需核心技能，每天 1 小时，2 个月完成');
      actionPath.shortTerm.push('参加相关培训课程，提升专业知识');
      actionPath.shortTerm.push('建立行业人脉，了解行业动态');
      
      // 中期（3-6个月）
      actionPath.midTerm.push('积累相关工作经验，参与实际项目');
      actionPath.midTerm.push('针对目标岗位要求，进行技能补强');
      actionPath.midTerm.push('建立专业作品集或案例集');
      
      // 长期（6-12个月）
      actionPath.longTerm.push('优化简历和作品集，突出核心技能和经验');
      actionPath.longTerm.push('准备面试，练习常见问题和专业知识');
      actionPath.longTerm.push('制定投递策略，优先选择符合条件的公司');
      break;
  }
  
  // 步骤三：输出内容自检
  // 确保行动路径与岗位类型匹配
  const isValidActionPath = validateActionPath(actionPath, industryType);
  if (!isValidActionPath) {
    // 如果不匹配，重新生成行动路径
    switch (industryType) {
      case '行政类':
        actionPath.shortTerm = ['学习 Excel 高级函数', '学习 PPT 制作', '学习 OA 系统操作', '准备人力资源管理师证'];
        actionPath.midTerm = ['积累大厂行政经验', '学习钉钉/企业微信管理', '提升会议组织能力', '学习供应商管理'];
        actionPath.longTerm = ['准备面试话术', '制定投递策略', '整理行政工作案例'];
        break;
      case '技术类':
        actionPath.shortTerm = ['学习编程语言', '刷 LeetCode 题目', '学习相关框架'];
        actionPath.midTerm = ['完成项目并上传 GitHub', '参与开源项目', '学习系统设计'];
        actionPath.longTerm = ['准备技术面试', '整理作品集', '学习新技术'];
        break;
      default:
        // 保持原有路径
        break;
    }
  }
  
  // 生成竞争力度分析
  const competitionAnalysis = {
    supplyDemand: positionLower.includes('前端') || positionLower.includes('产品') ? '竞争激烈' : positionLower.includes('后端') ? '竞争适中' : '竞争宽松',
    competitorProfile: positionLower.includes('前端') ? '计算机相关专业本科，1-3年前端经验，熟悉主流框架' : positionLower.includes('后端') ? '计算机相关专业本科，2-3年后端经验，熟悉至少一种后端语言' : positionLower.includes('产品') ? '本科及以上学历，2-3年产品经验，有成功产品案例' : '相关专业背景，1-2年相关经验，具备基本技能',
    userCompetitiveness: {
      strengths: experienceYears > 0 ? '有一定工作经验' : '学习能力强，可塑性高',
      weaknesses: skills.length < 3 ? '技能储备不足' : experienceYears < 2 ? '项目经验不足' : '需要更深入的专业知识'
    }
  };
  
  // 生成晋升路径预览
  const promotionPath = [];
  // 使用岗位调研结果中的晋升路径
  const researchPath = positionResearch.promotionPath;
  if (researchPath.length > 0) {
    // 将调研结果转换为路径格式
    promotionPath.push(researchPath.join(' → '));
  } else {
    // 默认路径
    if (positionLower.includes('前端')) {
      promotionPath.push('初级前端工程师 → 中级前端工程师 → 高级前端工程师 → 前端技术负责人');
    } else if (positionLower.includes('后端')) {
      promotionPath.push('初级后端工程师 → 中级后端工程师 → 高级后端工程师 → 后端技术负责人');
    } else if (positionLower.includes('产品')) {
      promotionPath.push('产品助理 → 产品经理 → 高级产品经理 → 产品总监');
    } else if (positionLower.includes('运营')) {
      promotionPath.push('运营专员 → 运营主管 → 运营经理 → 运营总监');
    } else {
      promotionPath.push('初级岗位 → 中级岗位 → 高级岗位 → 管理岗位');
    }
  }
  
  // 生成能力对比表格（保持向后兼容）
  const abilityComparison = gapAnalysis.map(item => ({
    dimension: item.dimension,
    requirement: item.target,
    current: item.current,
    gap: item.gap === '小' ? '达标' : '缺口'
  }));
  
  // 生成具体行动计划（保持向后兼容）
  const actionPlans = [...actionPath.shortTerm, ...actionPath.midTerm];
  
  // 评估达成时间
  let estimatedTime = '6-12个月';
  let timeReasoning = '基于以下因素估算：';
  
  // 计算缺口数量
  const gapCount = gapAnalysis.filter(item => item.gap === '大' || item.gap === '中').length;
  
  if (gapCount === 0) {
    estimatedTime = '3-6个月';
    timeReasoning = '基于以下因素估算：\n1. 所有能力维度都已达标\n2. 主要需要积累项目经验和准备面试\n3. 预计 3-6 个月可以完成求职准备';
  } else if (gapCount <= 2) {
    estimatedTime = '6-12个月';
    timeReasoning = '基于以下因素估算：\n1. 有 1-2 个能力缺口需要弥补\n2. 需要系统学习相关技能并完成项目\n3. 同时需要积累工作经验和准备面试\n4. 预计 6-12 个月可以达到目标';
  } else if (gapCount <= 4) {
    estimatedTime = '1-2年';
    timeReasoning = '基于以下因素估算：\n1. 有 3-4 个能力缺口需要弥补\n2. 需要系统学习多项技能并完成多个项目\n3. 同时需要积累工作经验\n4. 预计 1-2 年可以达到目标';
  } else {
    estimatedTime = '2年以上';
    timeReasoning = '基于以下因素估算：\n1. 有 5 个或更多能力缺口需要弥补\n2. 需要全面系统地学习多项技能\n3. 需要大量项目经验积累\n4. 可能需要跨行转岗，学习成本较高\n5. 预计需要 2 年以上时间达到目标';
  }
  
  // 生成差距列表（保持向后兼容）
  const gaps = gapAnalysis
    .filter(item => item.gap === '大' || item.gap === '中')
    .map(item => `${item.dimension}：${item.target}`);
  
  // 根据用户经验生成个性化行动计划（保持向后兼容）
  const shortTermPlan = [];
  if (experienceYears === 0) {
    shortTermPlan.push('1个月：系统学习目标岗位基础技能，完成1-2个入门项目');
    shortTermPlan.push('2个月：参与开源项目或实习，积累实战经验');
    shortTermPlan.push('3个月：准备简历和作品集，开始投递实习或初级岗位');
  } else if (experienceYears < 3) {
    shortTermPlan.push('1个月：深入学习目标岗位所需核心技术，完成2-3个实战项目');
    shortTermPlan.push('2个月：优化简历和作品集，针对性投递 20-30 家公司');
    shortTermPlan.push('3个月：面试复盘和技能查漏补缺，争取拿到意向 offer');
  } else {
    shortTermPlan.push('1个月：对标目标岗位要求，进行技能补强');
    shortTermPlan.push('2个月：准备跳槽材料，联系猎头和内推');
    shortTermPlan.push('3个月：集中面试，争取更高薪资和职位');
  }
  
  const midTermPlan = [];
  if (experienceYears < 2) {
    midTermPlan.push('第1年：快速适应职场，掌握工作所需技能');
    midTermPlan.push('第1.5年：开始独立负责项目模块，积累经验');
    midTermPlan.push('第2年：争取晋升到高级职位，或跳槽到更好的平台');
  } else {
    midTermPlan.push('第1年：快速熟悉新公司业务，争取独立负责重要模块');
    midTermPlan.push('第1.5年：积累 2-3 个有影响力的项目经验');
    midTermPlan.push('第2年：争取晋升机会或跳槽到更高平台');
  }
  
  const longTermPlan = [];
  if (positionLower.includes('技术')) {
    longTermPlan.push('3-5年：成为技术专家，带领团队或负责核心系统');
    longTermPlan.push('5年以上：技术总监或架构师，参与技术决策');
  } else if (positionLower.includes('产品')) {
    longTermPlan.push('3-5年：产品总监，负责产品线规划');
    longTermPlan.push('5年以上：首席产品官或创业');
  } else if (positionLower.includes('运营')) {
    longTermPlan.push('3-5年：运营总监，负责整体运营策略');
    longTermPlan.push('5年以上：业务负责人或独立创业');
  } else {
    longTermPlan.push('3-5年：成为领域内资深专家或技术/产品负责人');
    longTermPlan.push('5年以上：建立个人行业影响力，向更高职业目标迈进');
  }
  
  // 步骤四：输出内容校验
  // 确保组织架构符合行业特征
  companyStructure = validateCompanyStructure(companyStructure, industryType);
  
  return {
    targetJob: survey.targetPosition,
    matchedJobs: [],
    companyStructure,
    requirements,
    salaryRange,
    salaryAnalysis: {
      min: 15000,
      max: 45000,
      avg: 25000,
      median: 22000
    },
    competition,
    gaps,
    difficulty,
    shortTermPlan,
    midTermPlan,
    longTermPlan,
    abilityComparison,
    actionPlans,
    estimatedTime,
    timeReasoning,
    hardSkills,
    softSkills,
    companyRequirements,
    gapAnalysis,
    actionPath,
    competitionAnalysis,
    promotionPath,
    skillRecommendations: []
  };
}

// 辅助函数：获取岗位职责
function getPositionResponsibilities(position: string): string[] {
  const positionLower = position.toLowerCase();
  
  if (positionLower.includes('前端') || positionLower.includes('web')) {
    return [
      '负责网站/应用前端开发',
      '实现用户界面和交互功能',
      '优化前端性能和用户体验',
      '与后端团队协作实现功能',
      '维护和更新现有前端代码'
    ];
  } else if (positionLower.includes('后端')) {
    return [
      '负责服务器端应用开发',
      '设计和实现数据库结构',
      '开发和维护API接口',
      '处理业务逻辑和数据处理',
      '确保系统性能和安全性'
    ];
  } else if (positionLower.includes('产品')) {
    return [
      '负责产品规划和设计',
      '收集和分析用户需求',
      '制定产品路线图',
      '与开发团队协作实现产品功能',
      '监控产品性能和用户反馈'
    ];
  } else if (positionLower.includes('运营')) {
    return [
      '负责产品运营策略制定',
      '执行用户增长和 retention 活动',
      '分析运营数据和用户行为',
      '与产品和开发团队协作优化产品',
      '管理运营预算和资源'
    ];
  } else if (positionLower.includes('设计')) {
    return [
      '负责产品界面设计',
      '创建视觉设计和交互原型',
      '与产品和开发团队协作',
      '维护设计系统和规范',
      '持续优化用户体验'
    ];
  } else if (positionLower.includes('项目经理')) {
    return [
      '负责项目规划和执行',
      '管理项目进度和资源',
      '协调跨团队合作',
      '风险管理和问题解决',
      '确保项目按时交付'
    ];
  } else {
    return [
      '负责相关业务领域的工作',
      '完成上级交办的任务',
      '与团队成员协作',
      '持续学习和提升技能',
      '为公司发展贡献力量'
    ];
  }
}

// 辅助函数：获取岗位技能要求
function getRequiredSkills(position: string): string[] {
  const positionLower = position.toLowerCase();
  
  if (positionLower.includes('前端') || positionLower.includes('web')) {
    return [
      'HTML/CSS/JavaScript',
      'React/Vue/Angular',
      '前端工程化工具',
      '响应式设计',
      '浏览器兼容性'
    ];
  } else if (positionLower.includes('后端')) {
    return [
      'Java/Python/Go',
      'Spring/Django/Flask',
      'MySQL/PostgreSQL',
      '微服务架构',
      'DevOps工具'
    ];
  } else if (positionLower.includes('产品')) {
    return [
      '产品设计工具（Axure/Figma）',
      '数据分析能力',
      '用户研究方法',
      '项目管理能力',
      '沟通协调能力'
    ];
  } else if (positionLower.includes('运营')) {
    return [
      '数据分析能力',
      '文案写作能力',
      '活动策划能力',
      '用户增长策略',
      '社交媒体运营'
    ];
  } else if (positionLower.includes('设计')) {
    return [
      'UI/UX设计能力',
      'Figma/Sketch/Adobe XD',
      '视觉设计基础',
      '交互设计原则',
      '设计系统知识'
    ];
  } else if (positionLower.includes('项目经理')) {
    return [
      '项目管理方法论',
      '敏捷开发流程',
      '风险管理能力',
      '沟通协调能力',
      'PMP/Prince2认证'
    ];
  } else {
    return [
      '相关领域专业知识',
      '基本办公软件技能',
      '沟通能力',
      '团队协作能力',
      '问题解决能力'
    ];
  }
}

// 辅助函数：获取公司特定要求
function getCompanySpecificRequirements(company: string, position: string): string[] {
  const companyLower = company.toLowerCase();
  const positionLower = position.toLowerCase();
  
  if (companyLower.includes('阿里') || companyLower.includes('alibaba')) {
    return [
      '有大型电商平台经验优先',
      '熟悉阿里技术栈',
      '具备良好的团队协作能力',
      '有较强的学习能力和适应能力',
      '能承受一定的工作压力'
    ];
  } else if (companyLower.includes('腾讯') || companyLower.includes('tencent')) {
    return [
      '有社交产品或游戏经验优先',
      '熟悉腾讯技术栈',
      '具备良好的沟通能力',
      '有创新思维和解决问题的能力',
      '对互联网产品有浓厚兴趣'
    ];
  } else if (companyLower.includes('字节') || companyLower.includes('bytedance')) {
    return [
      '有内容平台或短视频经验优先',
      '熟悉字节技术栈',
      '具备快速学习能力',
      '有较强的抗压能力',
      '对产品和用户体验有深刻理解'
    ];
  } else if (companyLower.includes('百度') || companyLower.includes('baidu')) {
    return [
      '有搜索引擎或AI相关经验优先',
      '熟悉百度技术栈',
      '具备扎实的技术基础',
      '有较强的问题解决能力',
      '对技术创新有热情'
    ];
  } else if (companyLower.includes('京东') || companyLower.includes('jd')) {
    return [
      '有电商或物流相关经验优先',
      '熟悉京东技术栈',
      '具备良好的团队合作精神',
      '有较强的执行力',
      '对零售行业有了解'
    ];
  } else if (companyLower.includes('美团') || companyLower.includes('meituan')) {
    return [
      '有本地生活服务相关经验优先',
      '熟悉美团技术栈',
      '具备良好的沟通协调能力',
      '有较强的用户思维',
      '对O2O行业有了解'
    ];
  } else {
    return [
      '有相关行业经验优先',
      '具备良好的专业技能',
      '有较强的学习能力',
      '具备良好的团队协作能力',
      '对公司业务有浓厚兴趣'
    ];
  }
}

// 辅助函数：获取晋升路径
function getPromotionPath(position: string): string[] {
  const positionLower = position.toLowerCase();
  
  if (positionLower.includes('前端')) {
    return [
      '初级前端工程师',
      '中级前端工程师',
      '高级前端工程师',
      '前端技术负责人',
      '技术总监'
    ];
  } else if (positionLower.includes('后端')) {
    return [
      '初级后端工程师',
      '中级后端工程师',
      '高级后端工程师',
      '后端技术负责人',
      '技术总监'
    ];
  } else if (positionLower.includes('产品')) {
    return [
      '产品助理',
      '产品经理',
      '高级产品经理',
      '产品总监',
      '首席产品官'
    ];
  } else if (positionLower.includes('运营')) {
    return [
      '运营专员',
      '运营主管',
      '运营经理',
      '运营总监',
      'COO'
    ];
  } else if (positionLower.includes('设计')) {
    return [
      '初级设计师',
      '中级设计师',
      '高级设计师',
      '设计总监',
      '创意总监'
    ];
  } else if (positionLower.includes('项目经理')) {
    return [
      '助理项目经理',
      '项目经理',
      '高级项目经理',
      '项目总监',
      'PMO负责人'
    ];
  } else {
    return [
      '初级岗位',
      '中级岗位',
      '高级岗位',
      '管理岗位',
      '高级管理岗位'
    ];
  }
}

// 辅助函数：识别行业类型
function identifyIndustryType(position: string): string {
  const positionLower = position.toLowerCase();
  
  if (positionLower.includes('设计') || positionLower.includes('ui') || positionLower.includes('ux') || positionLower.includes('视觉') || positionLower.includes('平面')) {
    return '设计类';
  } else if (positionLower.includes('前端') || positionLower.includes('后端') || positionLower.includes('开发') || positionLower.includes('工程师') || positionLower.includes('程序员') || positionLower.includes('数据')) {
    return '技术类';
  } else if (positionLower.includes('运营') || positionLower.includes('市场') || positionLower.includes('推广') || positionLower.includes('用户') || positionLower.includes('内容')) {
    return '运营类';
  } else if (positionLower.includes('经理') || positionLower.includes('管理') || positionLower.includes('总监') || positionLower.includes('主管')) {
    return '管理类';
  } else if (positionLower.includes('行政') || positionLower.includes('前台')) {
    return '行政类';
  } else if (positionLower.includes('hr') || positionLower.includes('招聘') || positionLower.includes('人事')) {
    return 'HR类';
  } else if (positionLower.includes('财务') || positionLower.includes('会计') || positionLower.includes('出纳')) {
    return '财务类';
  } else {
    return '其他类';
  }
}

// 辅助函数：校准用户技能
function calibrateUserSkills(skills: string, experienceYears: number): string {
  // 根据工作经验调整技能水平评估
  if (experienceYears >= 10) {
    // 10年经验的用户，技能水平应该较高
    return skills + ' 精通';
  } else if (experienceYears >= 5) {
    // 5-9年经验的用户，技能水平应该中等偏上
    return skills + ' 熟练';
  } else if (experienceYears >= 2) {
    // 2-4年经验的用户，技能水平应该中等
    return skills + ' 掌握';
  } else {
    // 1年以下经验的用户，技能水平应该较低
    return skills;
  }
}

// 辅助函数：验证组织架构
function validateCompanyStructure(companyStructure: string[], industryType: string): string[] {
  // 根据行业类型调整组织架构
  if (industryType === '设计类') {
    return [
      '设计部 - UI/UX设计团队',
      '创意部 - 创意设计团队',
      '品牌部 - 品牌设计团队',
      '产品部 - 产品设计团队',
      '市场部 - 营销设计团队'
    ];
  } else if (industryType === '技术类') {
    return [
      '研发部 - 产品研发团队',
      '技术部 - 前端/后端开发',
      '产品部 - 产品设计团队',
      '测试部 - 质量保证团队',
      '运维部 - 系统运维团队'
    ];
  } else if (industryType === '运营类') {
    return [
      '运营部 - 用户运营团队',
      '市场部 - 品牌营销团队',
      '内容部 - 内容创作团队',
      '增长部 - 用户增长团队',
      '客服部 - 客户服务团队'
    ];
  } else if (industryType === '管理类') {
    return [
      '管理层 - 决策团队',
      '项目管理部 - 项目执行团队',
      '人力资源部 - 人才管理团队',
      '财务部 - 财务管理团队',
      '行政部 - 综合管理团队'
    ];
  } else if (industryType === '行政类') {
    return [
      '行政部 - 综合管理团队',
      '人力资源部 - 人才管理团队',
      '财务部 - 财务管理团队',
      '后勤部 - 物资管理团队',
      '法务部 - 法律事务团队'
    ];
  } else if (industryType === 'HR类') {
    return [
      '人力资源部 - 招聘团队',
      '人力资源部 - 薪酬福利团队',
      '人力资源部 - 培训发展团队',
      '人力资源部 - 员工关系团队',
      '行政部 - 综合管理团队'
    ];
  } else if (industryType === '财务类') {
    return [
      '财务部 - 会计团队',
      '财务部 - 出纳团队',
      '财务部 - 税务团队',
      '财务部 - 审计团队',
      '财务部 - 预算团队'
    ];
  } else {
    return companyStructure;
  }
}

// 辅助函数：验证行动路径
function validateActionPath(actionPath: { shortTerm: string[]; midTerm: string[]; longTerm: string[]; }, industryType: string): boolean {
  // 检查行动路径是否与岗位类型匹配
  switch (industryType) {
    case '行政类':
      // 行政类岗位不应该有 GitHub 或项目相关的行动
      return !actionPath.shortTerm.some(action => action.includes('GitHub') || action.includes('项目')) &&
             !actionPath.midTerm.some(action => action.includes('GitHub') || action.includes('项目')) &&
             !actionPath.longTerm.some(action => action.includes('GitHub') || action.includes('项目'));
    case '技术类':
      // 技术类岗位应该有编程和项目相关的行动
      return actionPath.shortTerm.some(action => action.includes('编程') || action.includes('LeetCode')) &&
             actionPath.midTerm.some(action => action.includes('项目') || action.includes('GitHub'));
    case '设计类':
      // 设计类岗位应该有设计软件和作品集相关的行动
      return actionPath.shortTerm.some(action => action.includes('设计') || action.includes('软件')) &&
             actionPath.midTerm.some(action => action.includes('作品集') || action.includes('设计比赛'));
    case '运营类':
      // 运营类岗位应该有数据分析和账号运营相关的行动
      return actionPath.shortTerm.some(action => action.includes('数据') || action.includes('账号')) &&
             actionPath.midTerm.some(action => action.includes('案例') || action.includes('数据'));
    case 'HR类':
      // HR类岗位应该有招聘和人力资源相关的行动
      return actionPath.shortTerm.some(action => action.includes('招聘') || action.includes('人力资源')) &&
             actionPath.midTerm.some(action => action.includes('招聘') || action.includes('ATS'));
    case '财务类':
      // 财务类岗位应该有财务软件和考证相关的行动
      return actionPath.shortTerm.some(action => action.includes('财务') || action.includes('会计证')) &&
             actionPath.midTerm.some(action => action.includes('财务') || action.includes('报表'));
    default:
      return true;
  }
}

