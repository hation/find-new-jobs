#!/usr/bin/env node

/**
 * job-search 到 GBrain 集成适配器
 * 将招聘搜索查询和结果存入 GBrain 知识图谱
 * 
 * 支持的数据:
 * 1. 招聘搜索历史
 * 2. 职位详细信息
 * 3. 公司信息
 * 4. 薪资分布
 * 5. 技能要求
 */

const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const { promisify } = require('util');

const execAsync = promisify(exec);

class JobToGBrainAdapter {
  constructor(config = {}) {
    this.config = {
      gbrainPath: config.gbrainPath || 'gbrain',
      gbrainHome: config.gbrainHome || path.join(process.env.HOME, '.gbrain'),
      jobDataDir: config.jobDataDir || path.join(process.env.HOME, '.openclaw/job-data'),
      jobCacheDir: config.jobCacheDir || path.join(process.env.HOME, '.openclaw/job-cache'),
      verbose: config.verbose || false,
      autoSave: config.autoSave || true,
      ...config
    };
    
    this.log(`💼 JobToGBrainAdapter 初始化完成`, 'info');
    this.log(`🔧 GBrain 路径: ${this.config.gbrainPath}`, 'debug');
    this.log(`📁 招聘数据目录: ${this.config.jobDataDir}`, 'debug');
    this.log(`📦 招聘缓存目录: ${this.config.jobCacheDir}`, 'debug');
    
    // 确保目录存在
    this.ensureDirectories();
  }
  
  ensureDirectories() {
    const dirs = [
      this.config.jobDataDir,
      this.config.jobCacheDir,
      path.join(this.config.jobCacheDir, 'searches'),
      path.join(this.config.jobCacheDir, 'positions'),
      path.join(this.config.jobCacheDir, 'companies'),
      path.join(this.config.jobCacheDir, 'analytics'),
      path.join(this.config.gbrainHome, 'logs/job-search')
    ];
    
    dirs.forEach(dir => {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
        this.log(`📁 创建目录: ${dir}`, 'debug');
      }
    });
  }
  
  log(message, level = 'info') {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] [${level.toUpperCase()}] ${message}`;
    
    if (this.config.verbose || level === 'error' || level === 'warn') {
      const colors = {
        info: '\x1b[36m',
        debug: '\x1b[90m',
        warn: '\x1b[33m',
        error: '\x1b[31m',
        success: '\x1b[32m'
      };
      
      const color = colors[level] || colors.info;
      const reset = '\x1b[0m';
      
      if (level === 'success') {
        console.log(`✅ ${message}`);
      } else if (level === 'error') {
        console.error(`❌ ${message}`);
      } else if (level === 'warn') {
        console.warn(`⚠️  ${message}`);
      } else if (level === 'debug') {
        if (this.config.verbose) {
          console.log(`${color}${message}${reset}`);
        }
      } else {
        console.log(`${color}${message}${reset}`);
      }
    }
    
    // 记录到文件
    const logFile = path.join(this.config.gbrainHome, 'logs/job-search/job-adapter.log');
    try {
      fs.appendFileSync(logFile, logMessage + '\n');
    } catch (error) {
      // 忽略文件日志错误
    }
  }
  
  /**
   * 解析招聘数据
   */
  async parseJobData(jobData) {
    try {
      this.log(`📄 解析招聘数据...`, 'info');
      
      let parsedData;
      
      if (typeof jobData === 'string') {
        // 如果是字符串，尝试解析为 JSON
        try {
          parsedData = JSON.parse(jobData);
        } catch (jsonError) {
          // 如果不是 JSON，当作简单搜索查询
          parsedData = this.parseSimpleJobQuery(jobData);
        }
      } else if (typeof jobData === 'object') {
        parsedData = jobData;
      } else {
        throw new Error(`不支持的招聘数据类型: ${typeof jobData}`);
      }
      
      // 增强数据
      parsedData = this.enhanceJobData(parsedData);
      
      this.log(`📊 解析完成: ${parsedData.query || parsedData.jobName || parsedData.id}`, 'success');
      return parsedData;
      
    } catch (error) {
      throw new Error(`解析招聘数据失败: ${error.message}`);
    }
  }
  
  /**
   * 解析简单招聘查询
   */
  parseSimpleJobQuery(query) {
    const jobId = `job_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    return {
      id: jobId,
      query: query,
      source: 'boss-zhipin',
      format: 'simple_query',
      rawQuery: query,
      parsedAt: new Date().toISOString(),
      metadata: {
        type: 'job_search',
        source: 'job-search-skill',
        processingTime: Date.now()
      }
    };
  }
  
  /**
   * 增强招聘数据
   */
  enhanceJobData(jobData) {
    // 确保必要字段
    if (!jobData.id) {
      jobData.id = `job_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    if (!jobData.source) {
      jobData.source = 'boss-zhipin';
    }
    
    if (!jobData.parsedAt) {
      jobData.parsedAt = new Date().toISOString();
    }
    
    // 分析查询
    if (jobData.query) {
      jobData.queryAnalysis = this.analyzeJobQuery(jobData.query);
      
      // 提取关键词
      jobData.keywords = this.extractJobKeywords(jobData.query);
      
      // 分析职位类型
      jobData.jobType = this.analyzeJobType(jobData.query);
      
      // 分析技能要求
      jobData.skills = this.extractSkills(jobData.query);
    }
    
    // 分析职位信息
    if (jobData.jobName) {
      jobData.positionAnalysis = this.analyzePosition(jobData);
    }
    
    // 分析薪资
    if (jobData.salaryDesc || jobData.salary) {
      jobData.salaryAnalysis = this.analyzeSalary(jobData.salaryDesc || jobData.salary);
    }
    
    // 提取公司信息
    if (jobData.brandName) {
      jobData.companyAnalysis = this.analyzeCompany(jobData);
    }
    
    // 添加元数据
    jobData.metadata = {
      ...jobData.metadata,
      processedBy: 'job-to-gbrain-adapter',
      adapterVersion: '1.0.0',
      processingTime: new Date().toISOString()
    };
    
    return jobData;
  }
  
  /**
   * 分析招聘查询
   */
  analyzeJobQuery(query) {
    const analysis = {
      length: query.length,
      wordCount: this.countWords(query),
      complexity: 'simple',
      language: this.detectLanguage(query),
      hasLocation: this.hasLocation(query),
      hasExperience: this.hasExperience(query),
      hasSalary: this.hasSalary(query)
    };
    
    // 分析复杂度
    const words = query.split(/\s+/).length;
    if (words > 3) analysis.complexity = 'medium';
    if (words > 6) analysis.complexity = 'complex';
    
    return analysis;
  }
  
  /**
   * 统计字数
   */
  countWords(text) {
    // 中文汉字
    const chinese = (text.match(/[\u4e00-\u9fa5]/g) || []).length;
    // 英文单词
    const english = (text.match(/\b[a-zA-Z]+\b/g) || []).length;
    // 数字
    const numbers = (text.match(/\b\d+\b/g) || []).length;
    
    return chinese + english + numbers;
  }
  
  /**
   * 检测语言
   */
  detectLanguage(text) {
    // 简单的中英文检测
    const chineseChars = (text.match(/[\u4e00-\u9fa5]/g) || []).length;
    const englishChars = (text.match(/[a-zA-Z]/g) || []).length;
    
    if (chineseChars > englishChars) {
      return 'chinese';
    } else if (englishChars > chineseChars) {
      return 'english';
    } else {
      return 'mixed';
    }
  }
  
  /**
   * 检查是否包含地点
   */
  hasLocation(query) {
    const locations = ['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '南京', '西安', '长沙'];
    return locations.some(location => query.includes(location));
  }
  
  /**
   * 检查是否包含经验要求
   */
  hasExperience(query) {
    const experienceTerms = ['应届', '经验不限', '1-3年', '3-5年', '5-10年', '10年以上', '经验'];
    return experienceTerms.some(term => query.includes(term));
  }
  
  /**
   * 检查是否包含薪资
   */
  hasSalary(query) {
    const salaryPatterns = [/\d+K/, /\d+-\d+K/, /\d+万/, /\d+-\d+万/, /面议/, /薪资/];
    return salaryPatterns.some(pattern => pattern.test(query));
  }
  
  /**
   * 提取招聘关键词
   */
  extractJobKeywords(query, limit = 10) {
    const words = query.toLowerCase()
      .replace(/[^\u4e00-\u9fa5a-zA-Z0-9\s]/g, ' ')
      .split(/\s+/)
      .filter(word => word.length > 1);
    
    const frequency = {};
    words.forEach(word => {
      frequency[word] = (frequency[word] || 0) + 1;
    });
    
    return Object.entries(frequency)
      .sort((a, b) => b[1] - a[1])
      .slice(0, limit)
      .map(([word]) => word);
  }
  
  /**
   * 分析职位类型
   */
  analyzeJobType(query) {
    const queryLower = query.toLowerCase();
    
    const jobTypes = {
      '技术': ['开发', '工程师', '程序员', '架构', '算法', 'AI', '人工智能', '机器学习', '前端', '后端', '全栈'],
      '产品': ['产品经理', '产品设计', '产品运营', '产品', 'PM'],
      '设计': ['设计师', 'UI', 'UX', '视觉', '交互'],
      '运营': ['运营', '推广', '营销', '市场', '销售', '商务'],
      '数据': ['数据分析', '数据科学', '数据挖掘', '大数据'],
      '测试': ['测试', 'QA', '质量保证'],
      '运维': ['运维', 'DevOps', '系统', '网络'],
      '管理': ['经理', '总监', '主管', '负责人', '领导'],
      '其他': ['助理', '专员', '顾问', '专家', '实习生']
    };
    
    for (const [type, patterns] of Object.entries(jobTypes)) {
      for (const pattern of patterns) {
        if (queryLower.includes(pattern.toLowerCase())) {
          return type;
        }
      }
    }
    
    return '其他';
  }
  
  /**
   * 提取技能
   */
  extractSkills(query) {
    const skills = [];
    const queryLower = query.toLowerCase();
    
    const skillPatterns = {
      '编程语言': ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'php', 'ruby', 'swift', 'kotlin'],
      '前端': ['react', 'vue', 'angular', 'html', 'css', 'sass', 'less', 'webpack', 'vite'],
      '后端': ['node.js', 'spring', 'django', 'flask', 'express', 'nestjs', 'laravel'],
      '数据库': ['mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle', 'sql server'],
      '云服务': ['aws', 'azure', 'gcp', '阿里云', '腾讯云', '华为云'],
      '容器': ['docker', 'kubernetes', '容器化', 'k8s'],
      'AI/ML': ['tensorflow', 'pytorch', '机器学习', '深度学习', '神经网络', '自然语言处理', '计算机视觉'],
      '大数据': ['hadoop', 'spark', 'hive', 'flink', 'kafka'],
      '移动端': ['android', 'ios', 'flutter', 'react native', '小程序'],
      '测试': ['selenium', 'jmeter', 'postman', '自动化测试', '单元测试']
    };
    
    for (const [category, skillList] of Object.entries(skillPatterns)) {
      for (const skill of skillList) {
        if (queryLower.includes(skill.toLowerCase())) {
          skills.push({
            skill: skill,
            category: category
          });
        }
      }
    }
    
    return skills.slice(0, 10);
  }
  
  /**
   * 分析职位
   */
  analyzePosition(jobData) {
    const analysis = {
      positionLevel: this.analyzePositionLevel(jobData),
      urgency: this.analyzeUrgency(jobData),
      popularity: this.analyzePopularity(jobData),
      requirements: this.extractRequirements(jobData)
    };
    
    return analysis;
  }
  
  /**
   * 分析职位级别
   */
  analyzePositionLevel(jobData) {
    const jobName = jobData.jobName || '';
    const jobNameLower = jobName.toLowerCase();
    
    if (jobNameLower.includes('实习生') || jobNameLower.includes('应届')) {
      return 'entry';
    } else if (jobNameLower.includes('资深') || jobNameLower.includes('高级') || jobNameLower.includes('senior')) {
      return 'senior';
    } else if (jobNameLower.includes('专家') || jobNameLower.includes('principal') || jobNameLower.includes('lead')) {
      return 'expert';
    } else if (jobNameLower.includes('经理') || jobNameLower.includes('主管') || jobNameLower.includes('manager')) {
      return 'manager';
    } else if (jobNameLower.includes('总监') || jobNameLower.includes('director')) {
      return 'director';
    } else if (jobNameLower.includes('vp') || jobNameLower.includes('副总裁') || jobNameLower.includes('c-level')) {
      return 'executive';
    } else {
      return 'mid';
    }
  }
  
  /**
   * 分析紧急程度
   */
  analyzeUrgency(jobData) {
    // 基于发布时间判断
    if (jobData.publishTime) {
      const publishDate = new Date(jobData.publishTime);
      const daysAgo = (Date.now() - publishDate.getTime()) / (1000 * 60 * 60 * 24);
      
      if (daysAgo < 1) return 'high';      // 1天内
      if (daysAgo < 3) return 'medium';    // 3天内
      if (daysAgo < 7) return 'low';       // 7天内
      return 'very_low';                   // 超过7天
    }
    
    return 'unknown';
  }
  
  /**
   * 分析受欢迎程度
   */
  analyzePopularity(jobData) {
    // 基于公司规模、薪资等判断
    let score = 0;
    
    // 公司规模加分
    const companySize = jobData.brandScaleName || '';
    if (companySize.includes('10000人以上') || companySize.includes('1000-9999人')) {
      score += 3;
    } else if (companySize.includes('500-999人') || companySize.includes('100-499人')) {
      score += 2;
    } else if (companySize.includes('20-99人')) {
      score += 1;
    }
    
    // 薪资加分
    if (jobData.salaryDesc) {
      if (jobData.salaryDesc.includes('30K') || jobData.salaryDesc.includes('3万')) {
        score += 3;
      } else if (jobData.salaryDesc.includes('20K') || jobData.salaryDesc.includes('2万')) {
        score += 2;
      } else if (jobData.salaryDesc.includes('10K') || jobData.salaryDesc.includes('1万')) {
        score += 1;
      }
    }
    
    // 经验要求加分（越宽松越受欢迎）
    const experience = jobData.jobExperience || '';
    if (experience.includes('经验不限') || experience.includes('应届')) {
      score += 2;
    } else if (experience.includes('1-3年')) {
      score += 1;
    }
    
    if (score >= 5) return 'high';
    if (score >= 3) return 'medium';
    return 'low';
  }
  
  /**
   * 提取要求
   */
  extractRequirements(jobData) {
    const requirements = [];
    
    // 学历要求
    if (jobData.jobDegree) {
      requirements.push(`学历: ${jobData.jobDegree}`);
    }
    
    // 经验要求
    if (jobData.jobExperience) {
      requirements.push(`经验: ${jobData.jobExperience}`);
    }
    
    // 技能要求（从职位描述中提取）
    if (jobData.jobDescription) {
      const desc = jobData.jobDescription.toLowerCase();
      
      const skillKeywords = [
        'python', 'java', 'javascript', 'react', 'vue', 'mysql', 'redis',
        'docker', 'kubernetes', 'aws', '阿里云', '腾讯云',
        '机器学习', '深度学习', '人工智能', '大数据'
      ];
      
      skillKeywords.forEach(skill => {
        if (desc.includes(skill.toLowerCase())) {
          requirements.push(`技能: ${skill}`);
        }
      });
    }
    
    return requirements.slice(0, 5);
  }
  
  /**
   * 分析薪资
   */
  analyzeSalary(salaryDesc) {
    if (!salaryDesc) return null;
    
    const analysis = {
      raw: salaryDesc,
      type: 'unknown',
      min: null,
      max: null,
      unit: 'monthly',
      estimatedAnnual: null
    };
    
    // 解析薪资范围
    const rangeMatch = salaryDesc.match(/(\d+)-(\d+)([K万])?/);
    if (rangeMatch) {
      analysis.min = parseInt(rangeMatch[1], 10);
      analysis.max = parseInt(rangeMatch[2], 10);
      analysis.unit = rangeMatch[3] === '万' ? 'monthly_wan' : 'monthly_k';
      
      // 转换到月薪千元
      if (analysis.unit === 'monthly_wan') {
        analysis.min *= 10;
        analysis.max *= 10;
        analysis.unit = 'monthly_k';
      }
      
      analysis.type = 'range';
      
      // 估算年薪（13薪）
      analysis.estimatedAnnual = Math.round((analysis.min + analysis.max) / 2 * 13);
    } else {
      // 单个薪资或面议
      const singleMatch = salaryDesc.match(/(\d+)([K万])/);
      if (singleMatch) {
        analysis.min = parseInt(singleMatch[1], 10);
        analysis.max = analysis.min;
        analysis.unit = singleMatch[2] === '万' ? 'monthly_wan' : 'monthly_k';
        
        if (analysis.unit === 'monthly_wan') {
          analysis.min *= 10;
          analysis.max *= 10;
          analysis.unit = 'monthly_k';
        }
        
        analysis.type = 'fixed';
        analysis.estimatedAnnual = Math.round(analysis.min * 13);
      } else if (salaryDesc.includes('面议')) {
        analysis.type = 'negotiable';
      }
    }
    
    return analysis;
  }
  
  /**
   * 分析公司
   */
  analyzeCompany(jobData) {
    const analysis = {
      size: this.parseCompanySize(jobData.brandScaleName),
      industry: jobData.brandIndustryName || '未知',
      stage: this.parseCompanyStage(jobData.brandStageName),
      reputation: this.estimateCompanyReputation(jobData)
    };
    
    return analysis;
  }
  
  /**
   * 解析公司规模
   */
  parseCompanySize(scaleName) {
    if (!scaleName) return 'unknown';
    
    const sizeMap = {
      '0-20人': 'micro',
      '20-99人': 'small',
      '100-499人': 'medium',
      '500-999人': 'large',
      '1000-9999人': 'enterprise',
      '10000人以上': 'mega'
    };
    
    return sizeMap[scaleName] || 'unknown';
  }
  
  /**
   * 解析公司阶段
   */
  parseCompanyStage(stageName) {
    if (!stageName) return 'unknown';
    
    const stageMap = {
      '未融资': 'seed',
      '天使轮': 'angel',
      'A轮': 'series_a',
      'B轮': 'series_b', 
      'C轮': 'series_c',
      'D轮及以上': 'series_d_plus',
      '已上市': 'public',
      '不需要融资': 'no_funding'
    };
    
    return stageMap[stageName] || 'unknown';
  }
  
  /**
   * 估计公司声誉
   */
  estimateCompanyReputation(jobData) {
    let score = 0;
    
    // 公司规模加分
    const size = this.parseCompanySize(jobData.brandScaleName);
    if (size === 'mega') score += 3;
    else if (size === 'enterprise') score += 2;
    else if (size === 'large') score += 1;
    
    // 融资阶段加分
    const stage = this.parseCompanyStage(jobData.brandStageName);
    if (stage === 'public') score += 3;
    else if (stage === 'series_d_plus') score += 2;
    else if (stage === 'series_c') score += 1;
    
    // 行业加分（科技行业通常声誉更好）
    const industry = jobData.brandIndustryName || '';
    if (industry.includes('互联网') || industry.includes('科技') || industry.includes('软件')) {
      score += 1;
    }
    
    if (score >= 5) return 'excellent';
    if (score >= 3) return 'good';
    if (score >= 1) return 'fair';
    return 'unknown';
  }
  
  /**
   * 保存招聘数据到 GBrain
   */
  async saveJobToGBrain(jobData, options = {}) {
    try {
      this.log(`💼 保存招聘数据到 GBrain: ${jobData.jobName || jobData.query || jobData.id}`, 'info');
      
      // 构建 GBrain 页面数据
      const pageData = {
        type: 'job',
        slug: this.generateJobSlug(jobData),
        title: this.generateJobTitle(jobData),
        body: this.generateJobBody(jobData),
        metadata: this.generateJobMetadata(jobData)
      };
      
      // 使用 GBrain CLI 添加页面
      const command = `${this.config.gbrainPath} add ${pageData.type} ${pageData.slug} \
        --title "${pageData.title.replace(/"/g, '\\"')}" \
        --body "${pageData.body.substring(0, 8000).replace(/"/g, '\\"')}"`;
      
      this.log(`🔧 执行命令: ${command.substring(0, 120)}...`, 'debug');
      
      const { stdout, stderr } = await execAsync(command, {
        env: {
          ...process.env,
          GBRAIN_HOME: this.config.gbrainHome
        },
        timeout: 30000 // 30秒超时
      });
      
      if (stderr && !stderr.includes('warning')) {
        throw new Error(`GBrain 命令错误: ${stderr}`);
      }
      
      // 解析返回的页面ID
      const pageIdMatch = stdout.match(/页面添加成功:\s*(\S+)/);
      const pageId = pageIdMatch ? pageIdMatch[1] : jobData.id;
      
      this.log(`✅ 招聘数据已保存到 GBrain: ${pageId}`, 'success');
      
      // 记录处理结果
      await this.recordJobProcessing(jobData, pageId, options);
      
      return {
        success: true,
        pageId: pageId,
        gbrainCommand: command,
        jobData: {
          id: jobData.id,
          jobName: jobData.jobName,
          company: jobData.brandName,
          salary: jobData.salaryDesc,
          location: jobData.cityName
        }
      };
      
    } catch (error) {
      this.log(`❌ 保存到 GBrain 失败: ${error.message}`, 'error');
      
      // 记录失败
      await this.recordJobFailure(jobData, error, options);
      
      throw error;
    }
  }
  
  /**
   * 生成招聘 slug
   */
  generateJobSlug(jobData) {
    let baseSlug;
    
    if (jobData.jobName) {
      baseSlug = jobData.jobName
        .toLowerCase()
        .replace(/[^\w\u4e00-\u9fa5]/g, '-')
        .replace(/-+/g, '-')
        .substring(0, 50);
    } else if (jobData.query) {
      baseSlug = jobData.query
        .toLowerCase()
        .replace(/[^\w\u4e00-\u9fa5]/g, '-')
        .replace(/-+/g, '-')
        .substring(0, 50);
    } else {
      baseSlug = `job-${jobData.id}`;
    }
    
    const datePart = jobData.parsedAt 
      ? new Date(jobData.parsedAt).toISOString().split('T')[0]
      : new Date().toISOString().split('T')[0];
    
    const locationPart = jobData.cityName 
      ? jobData.cityName.toLowerCase().replace(/[^\w\u4e00-\u9fa5]/g, '-')
      : 'unknown';
    
    const typePart = jobData.jobType || 'other';
    
    return `jobs/${datePart}/${locationPart}/${typePart}/${baseSlug}`;
  }
  
  /**
   * 生成招聘标题
   */
  generateJobTitle(jobData) {
    if (jobData.jobName) {
      return `${jobData.jobName} - ${jobData.brandName || '未知公司'}`;
    } else if (jobData.query) {
      return `招聘搜索: ${jobData.query}`;
    } else {
      return `招聘信息 ${jobData.id}`;
    }
  }
  
  /**
   * 生成招聘正文
   */
  generateJobBody(jobData) {
    const sections = [];
    
    // 头部信息
    sections.push(`# ${this.generateJobTitle(jobData)}`);
    sections.push('');
    
    if (jobData.jobName) {
      sections.push(`**职位名称**: ${jobData.jobName}`);
    }
    
    if (jobData.brandName) {
      sections.push(`**公司名称**: ${jobData.brandName}`);
    }
    
    if (jobData.cityName) {
      sections.push(`**工作地点**: ${jobData.cityName}`);
    }
    
    if (jobData.salaryDesc) {
      sections.push(`**薪资范围**: ${jobData.salaryDesc}`);
    }
    
    if (jobData.jobExperience) {
      sections.push(`**经验要求**: ${jobData.jobExperience}`);
    }
    
    if (jobData.jobDegree) {
      sections.push(`**学历要求**: ${jobData.jobDegree}`);
    }
    
    if (jobData.brandScaleName) {
      sections.push(`**公司规模**: ${jobData.brandScaleName}`);
    }
    
    if (jobData.brandIndustryName) {
      sections.push(`**行业领域**: ${jobData.brandIndustryName}`);
    }
    
    if (jobData.brandStageName) {
      sections.push(`**融资阶段**: ${jobData.brandStageName}`);
    }
    
    if (jobData.positionAnalysis?.positionLevel) {
      const levelMap = {
        'entry': '初级/应届',
        'mid': '中级',
        'senior': '高级',
        'expert': '专家',
        'manager': '经理/主管',
        'director': '总监',
        'executive': '高管'
      };
      sections.push(`**职位级别**: ${levelMap[jobData.positionAnalysis.positionLevel] || jobData.positionAnalysis.positionLevel}`);
    }
    
    if (jobData.positionAnalysis?.popularity) {
      const popularityMap = {
        'high': '🔥 热门',
        'medium': '🟡 中等',
        'low': '🟢 一般'
      };
      sections.push(`**受欢迎程度**: ${popularityMap[jobData.positionAnalysis.popularity] || jobData.positionAnalysis.popularity}`);
    }
    
    sections.push('');
    sections.push('---');
    sections.push('');
    
    // 职位描述
    if (jobData.jobDescription) {
      sections.push('## 职位描述');
      sections.push('');
      sections.push(jobData.jobDescription.substring(0, 2000));
      
      if (jobData.jobDescription.length > 2000) {
        sections.push('');
        sections.push('*(描述已截断，完整内容请查看原始文件)*');
      }
      sections.push('');
    }
    
    // 技能要求
    if (jobData.skills && jobData.skills.length > 0) {
      sections.push('## 技能要求');
      sections.push('');
      
      const skillsByCategory = {};
      jobData.skills.forEach(skill => {
        if (!skillsByCategory[skill.category]) {
          skillsByCategory[skill.category] = [];
        }
        skillsByCategory[skill.category].push(skill.skill);
      });
      
      Object.entries(skillsByCategory).forEach(([category, skillList]) => {
        sections.push(`### ${category}`);
        skillList.forEach(skill => {
          sections.push(`5. ${skill}`);
        });
        sections.push('');
      });
    }
    
    // 薪资分析
    if (jobData.salaryAnalysis) {
      sections.push('## 薪资分析');
      sections.push('');
      
      const analysis = jobData.salaryAnalysis;
      sections.push(`**薪资类型**: ${analysis.type === 'range' ? '范围薪资' : analysis.type === 'fixed' ? '固定薪资' : '面议'}`);
      
      if (analysis.min && analysis.max) {
        sections.push(`**月薪范围**: ${analysis.min}K - ${analysis.max}K`);
        if (analysis.estimatedAnnual) {
          sections.push(`**估算年薪**: 约 ${analysis.estimatedAnnual}K (按13薪计算)`);
        }
      } else if (analysis.min) {
        sections.push(`**月薪**: ${analysis.min}K`);
        if (analysis.estimatedAnnual) {
          sections.push(`**估算年薪**: 约 ${analysis.estimatedAnnual}K (按13薪计算)`);
        }
      }
      sections.push('');
    }
    
    // 公司分析
    if (jobData.companyAnalysis) {
      sections.push('## 公司分析');
      sections.push('');
      
      const analysis = jobData.companyAnalysis;
      const sizeMap = {
        'micro': '微型企业 (0-20人)',
        'small': '小型企业 (20-99人)',
        'medium': '中型企业 (100-499人)',
        'large': '大型企业 (500-999人)',
        'enterprise': '企业级 (1000-9999人)',
        'mega': '巨头企业 (10000人以上)'
      };
      
      const stageMap = {
        'seed': '未融资/种子期',
        'angel': '天使轮',
        'series_a': 'A轮',
        'series_b': 'B轮',
        'series_c': 'C轮',
        'series_d_plus': 'D轮及以上',
        'public': '已上市',
        'no_funding': '不需要融资'
      };
      
      const reputationMap = {
        'excellent': '⭐️⭐️⭐️⭐️⭐️ (优秀)',
        'good': '⭐️⭐️⭐️⭐️ (良好)',
        'fair': '⭐️⭐️⭐️ (一般)'
      };
      
      if (analysis.size !== 'unknown') {
        sections.push(`**公司规模**: ${sizeMap[analysis.size] || analysis.size}`);
      }
      
      if (analysis.industry !== '未知') {
        sections.push(`**行业领域**: ${analysis.industry}`);
      }
      
      if (analysis.stage !== 'unknown') {
        sections.push(`**融资阶段**: ${stageMap[analysis.stage] || analysis.stage}`);
      }
      
      if (analysis.reputation !== 'unknown') {
        sections.push(`**公司声誉**: ${reputationMap[analysis.reputation] || analysis.reputation}`);
      }
      sections.push('');
    }
    
    // 搜索分析（如果是搜索查询）
    if (jobData.query) {
      sections.push('## 搜索分析');
      sections.push('');
      
      if (jobData.queryAnalysis) {
        const analysis = jobData.queryAnalysis;
        sections.push(`**查询复杂度**: ${analysis.complexity}`);
        sections.push(`**查询语言**: ${analysis.language}`);
        sections.push(`**字数统计**: ${analysis.wordCount} 词`);
        sections.push(`**包含地点**: ${analysis.hasLocation ? '是' : '否'}`);
        sections.push(`**包含经验**: ${analysis.hasExperience ? '是' : '否'}`);
        sections.push(`**包含薪资**: ${analysis.hasSalary ? '是' : '否'}`);
      }
      
      if (jobData.keywords && jobData.keywords.length > 0) {
        sections.push(`**关键词**: ${jobData.keywords.slice(0, 5).join(', ')}`);
      }
      
      if (jobData.jobType) {
        sections.push(`**职位类型**: ${jobData.jobType}`);
      }
      sections.push('');
    }
    
    // 元数据
    sections.push('---');
    sections.push('');
    sections.push('## 元数据');
    sections.push('');
    sections.push(`**ID**: ${jobData.id}`);
    sections.push(`**来源**: ${jobData.source}`);
    sections.push(`**处理时间**: ${jobData.metadata?.processingTime || new Date().toISOString()}`);
    
    if (jobData.parsedAt) {
      sections.push(`**解析时间**: ${jobData.parsedAt}`);
    }
    
    if (jobData.publishTime) {
      sections.push(`**发布时间**: ${jobData.publishTime}`);
    }
    
    if (jobData.query) {
      sections.push(`**原始查询**: ${jobData.query}`);
    }
    
    return sections.join('\n');
  }
  
  /**
   * 生成招聘元数据
   */
  generateJobMetadata(jobData) {
    return {
      source: 'job-search-skill',
      jobId: jobData.id,
      jobName: jobData.jobName,
      company: jobData.brandName,
      location: jobData.cityName,
      salary: jobData.salaryDesc,
      experience: jobData.jobExperience,
      degree: jobData.jobDegree,
      jobType: jobData.jobType,
      skills: jobData.skills,
      positionLevel: jobData.positionAnalysis?.positionLevel,
      popularity: jobData.positionAnalysis?.popularity,
      companySize: jobData.companyAnalysis?.size,
      companyStage: jobData.companyAnalysis?.stage,
      processedAt: new Date().toISOString()
    };
  }
  
  /**
   * 记录招聘处理结果
   */
  async recordJobProcessing(jobData, pageId, options) {
    try {
      const logDir = path.join(this.config.gbrainHome, 'logs/job-search/processing');
      if (!fs.existsSync(logDir)) {
        fs.mkdirSync(logDir, { recursive: true });
      }
      
      const logFile = path.join(logDir, `processing-${new Date().toISOString().split('T')[0]}.jsonl`);
      
      const logEntry = {
        timestamp: new Date().toISOString(),
        jobId: jobData.id,
        gbrainPageId: pageId,
        jobName: jobData.jobName,
        company: jobData.brandName,
        salary: jobData.salaryDesc,
        location: jobData.cityName,
        status: 'success',
        processingTime: Date.now()
      };
      
      const logLine = JSON.stringify(logEntry) + '\n';
      fs.appendFileSync(logFile, logLine);
      
      this.log(`📝 记录处理日志: ${logFile}`, 'debug');
      
    } catch (error) {
      this.log(`⚠️  处理日志记录失败: ${error.message}`, 'warn');
    }
  }
  
  /**
   * 记录失败
   */
  async recordJobFailure(jobData, error, options) {
    try {
      const logDir = path.join(this.config.gbrainHome, 'logs/job-search/failures');
      if (!fs.existsSync(logDir)) {
        fs.mkdirSync(logDir, { recursive: true });
      }
      
      const logFile = path.join(logDir, `failures-${new Date().toISOString().split('T')[0]}.jsonl`);
      
      const logEntry = {
        timestamp: new Date().toISOString(),
        jobId: jobData.id,
        jobName: jobData.jobName,
        company: jobData.brandName,
        error: error.message,
        status: 'failed',
        processingTime: Date.now()
      };
      
      const logLine = JSON.stringify(logEntry) + '\n';
      fs.appendFileSync(logFile, logLine);
      
      this.log(`📝 记录失败日志: ${logFile}`, 'debug');
      
    } catch (logError) {
      // 忽略日志记录错误
    }
  }
  
  /**
   * 处理招聘数据
   */
  async processJobData(jobData, options = {}) {
    try {
      this.log(`🚀 开始处理招聘数据`, 'info');
      
      // 1. 解析招聘数据
      const parsedData = await this.parseJobData(jobData);
      
      // 2. 保存到 GBrain
      const saveResult = await this.saveJobToGBrain(parsedData, options);
      
      // 3. 创建备份（可选）
      if (options.backupDir) {
        await this.createJobBackup(parsedData, options.backupDir);
      }
      
      // 4. 保存到缓存（可选）
      if (options.saveToCache) {
        await this.saveJobToCache(parsedData);
      }
      
      this.log(`✅ 处理完成: ${parsedData.jobName || parsedData.query || parsedData.id}`, 'success');
      
      return {
        success: true,
        jobData: parsedData,
        gbrain: saveResult,
        options: options
      };
      
    } catch (error) {
      this.log(`❌ 处理失败: ${error.message}`, 'error');
      
      return {
        success: false,
        error: error.message,
        jobData: jobData,
        timestamp: new Date().toISOString()
      };
    }
  }
  
  /**
   * 创建招聘备份
   */
  async createJobBackup(jobData, backupDir) {
    try {
      if (!fs.existsSync(backupDir)) {
        fs.mkdirSync(backupDir, { recursive: true });
      }
      
      const backupFileName = `job_${jobData.id}_${Date.now()}.json`;
      const backupPath = path.join(backupDir, backupFileName);
      
      fs.writeFileSync(backupPath, JSON.stringify(jobData, null, 2));
      
      this.log(`📂 创建备份: ${backupPath}`, 'debug');
      
      return backupPath;
      
    } catch (error) {
      this.log(`⚠️  备份创建失败: ${error.message}`, 'warn');
      return null;
    }
  }
  
  /**
   * 保存招聘到缓存
   */
  async saveJobToCache(jobData) {
    try {
      const cacheFile = path.join(this.config.jobCacheDir, 'positions', `${jobData.id}.json`);
      
      const cacheData = {
        jobData: jobData,
        cachedAt: new Date().toISOString(),
        source: 'job-to-gbrain-adapter'
      };
      
      fs.writeFileSync(cacheFile, JSON.stringify(cacheData, null, 2));
      
      this.log(`💾 招聘数据已缓存: ${cacheFile}`, 'debug');
      
    } catch (error) {
      this.log(`⚠️  缓存保存失败: ${error.message}`, 'warn');
    }
  }
  
  /**
   * 批量处理招聘数据
   */
  async processJobDataBatch(jobDataList, options = {}) {
    const results = {
      total: jobDataList.length,
      success: 0,
      failed: 0,
      details: []
    };
    
    this.log(`📦 开始批量处理 ${jobDataList.length} 个招聘数据`, 'info');
    
    for (const [index, jobData] of jobDataList.entries()) {
      try {
        const jobName = typeof jobData === 'string' ? jobData : jobData.jobName || jobData.query;
        this.log(`💼 处理招聘 ${index + 1}/${jobDataList.length}: ${jobName?.substring(0, 50) || '无名称'}...`, 'info');
        
        const result = await this.processJobData(jobData, options);
        
        if (result.success) {
          results.success++;
          results.details.push({
            job: jobName || jobData.id,
            status: 'success',
            pageId: result.gbrain?.pageId,
            company: result.jobData?.brandName,
            salary: result.jobData?.salaryDesc,
            location: result.jobData?.cityName
          });
        } else {
          results.failed++;
          results.details.push({
            job: jobName || jobData.id,
            status: 'failed',
            error: result.error
          });
        }
        
        // 添加延迟，避免请求过快
        if (options.delayMs && index < jobDataList.length - 1) {
          await this.sleep(options.delayMs);
        }
        
      } catch (error) {
        results.failed++;
        results.details.push({
          job: typeof jobData === 'string' ? jobData : jobData.jobName || jobData.query || jobData.id,
          status: 'error',
          error: error.message
        });
        
        this.log(`❌ 处理招聘时发生错误: ${error.message}`, 'error');
      }
    }
    
    this.log(`📊 批量处理完成: 成功 ${results.success}, 失败 ${results.failed}`, 'info');
    
    // 生成报告
    await this.generateJobReport(results, options);
    
    return results;
  }
  
  /**
   * 生成招聘报告
   */
  async generateJobReport(results, options) {
    try {
      const reportDir = path.join(this.config.gbrainHome, 'reports/job-search');
      if (!fs.existsSync(reportDir)) {
        fs.mkdirSync(reportDir, { recursive: true });
      }
      
      const reportFile = path.join(reportDir, `report-${Date.now()}.json`);
      
      const report = {
        summary: {
          total: results.total,
          success: results.success,
          failed: results.failed,
          successRate: results.total > 0 ? (results.success / results.total * 100).toFixed(2) + '%' : '0%',
          processingTime: new Date().toISOString(),
          durationMs: Date.now() - (options.startTime || Date.now())
        },
        details: results.details,
        options: options,
        config: {
          gbrainPath: this.config.gbrainPath,
          gbrainHome: this.config.gbrainHome,
          jobDataDir: this.config.jobDataDir,
          jobCacheDir: this.config.jobCacheDir
        }
      };
      
      fs.writeFileSync(reportFile, JSON.stringify(report, null, 2));
      
      this.log(`📋 生成处理报告: ${reportFile}`, 'info');
      
      return reportFile;
      
    } catch (error) {
      this.log(`⚠️  报告生成失败: ${error.message}`, 'warn');
      return null;
    }
  }
  
  /**
   * 查询招聘历史
   */
  async queryJobHistory(query, options = {}) {
    try {
      this.log(`🔍 查询招聘历史: "${query}"`, 'info');
      
      const command = `${this.config.gbrainPath} query "${query}" --type job`;
      const { stdout, stderr } = await execAsync(command, {
        env: {
          ...process.env,
          GBRAIN_HOME: this.config.gbrainHome
        },
        timeout: 30000
      });
      
      if (stderr && !stderr.includes('warning')) {
        throw new Error(`查询失败: ${stderr}`);
      }
      
      // 解析查询结果
      const results = this.parseJobQueryResults(stdout);
      
      this.log(`✅ 查询完成: 找到 ${results.length} 个招聘记录`, 'success');
      
      return {
        success: true,
        query: query,
        results: results,
        rawOutput: stdout
      };
      
    } catch (error) {
      this.log(`❌ 查询失败: ${error.message}`, 'error');
      throw error;
    }
  }
  
  /**
   * 解析招聘查询结果
   */
  parseJobQueryResults(output) {
    const lines = output.split('\n').filter(line => line.trim().length > 0);
    const results = [];
    
    for (const line of lines) {
      // 匹配结果行: "1. [type] title (slug)"
      const match = line.match(/\s*(\d+)\.\s+\[(\w+)\]\s+(.+?)\s+\((\S+)\)/);
      
      if (match && match[2] === 'job') {
        results.push({
          index: parseInt(match[1]),
          type: match[2],
          title: match[3],
          slug: match[4]
        });
      }
    }
    
    return results;
  }
  
  /**
   * 睡眠函数
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
  
  /**
   * 命令行接口
   */
  async runCLI() {
    const args = process.argv.slice(2);
    
    if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
      console.log(`
💼 Job-to-GBrain 适配器

用法:
  node job-to-gbrain.js <命令> [参数]

命令:
  process <招聘数据>          处理招聘数据
  batch <文件路径>            批量处理招聘数据文件
  query <搜索词>              查询招聘历史
  history                    查看最近的招聘历史

示例:
  # 处理单个招聘查询
  node job-to-gbrain.js process '{"jobName": "AI开发工程师"}'
  
  # 处理招聘查询字符串
  node job-to-gbrain.js process "AI开发工程师 深圳"
  
  # 批量处理招聘数据文件
  node job-to-gbrain.js batch /path/to/job-data.json
  
  # 查询招聘历史
  node job-to-gbrain.js query "AI开发"
  
  # 查看招聘历史
  node job-to-gbrain.js history

选项:
  --verbose, -v             详细输出
  --delay-ms <ms>           处理间隔（毫秒）
  --backup-dir <dir>        备份目录
  --save-cache             保存到缓存
  --help, -h                显示帮助
  --version, -V             显示版本

环境变量:
  GBRAIN_HOME               GBrain 数据目录（默认: ~/.gbrain）
  GBRAIN_PATH               GBrain 命令路径（默认: gbrain）
  JOB_DATA_DIR              招聘数据目录（默认: ~/.openclaw/job-data）
  JOB_CACHE_DIR             招聘缓存目录（默认: ~/.openclaw/job-cache）
      `);
      process.exit(0);
    }
    
    if (args.includes('--version') || args.includes('-V')) {
      console.log('job-to-gbrain v1.0.0');
      process.exit(0);
    }
    
    // 解析命令
    const command = args[0];
    const commandArgs = args.slice(1).filter(arg => !arg.startsWith('--'));
    const options = this.parseCLIOptions(args);
    
    switch (command) {
      case 'process':
        await this.handleProcessCommand(commandArgs, options);
        break;
        
      case 'batch':
        await this.handleBatchCommand(commandArgs, options);
        break;
        
      case 'query':
        await this.handleQueryCommand(commandArgs, options);
        break;
        
      case 'history':
        await this.handleHistoryCommand(options);
        break;
        
      default:
        console.log(`❌ 未知命令: ${command}`);
        console.log('使用 --help 查看可用命令');
        process.exit(1);
    }
  }
  
  /**
   * 解析命令行选项
   */
  parseCLIOptions(args) {
    const options = {
      verbose: false,
      delayMs: 2000,
      backupDir: null,
      saveCache: false,
      startTime: Date.now()
    };
    
    for (let i = 0; i < args.length; i++) {
      const arg = args[i];
      
      if (arg === '--verbose' || arg === '-v') {
        options.verbose = true;
        this.config.verbose = true;
      } else if (arg === '--delay-ms') {
        options.delayMs = parseInt(args[++i], 10);
      } else if (arg === '--backup-dir') {
        options.backupDir = args[++i];
      } else if (arg === '--save-cache') {
        options.saveCache = true;
      }
    }
    
    return options;
  }
  
  /**
   * 处理 process 命令
   */
  async handleProcessCommand(args, options) {
    const jobData = args[0];
    
    if (!jobData) {
      console.log('❌ 需要提供招聘数据');
      process.exit(1);
    }
    
    const result = await this.processJobData(jobData, options);
    console.log(JSON.stringify(result, null, 2));
  }
  
  /**
   * 处理 batch 命令
   */
  async handleBatchCommand(args, options) {
    const filePath = args[0];
    
    if (!filePath) {
      console.log('❌ 需要提供文件路径');
      process.exit(1);
    }
    
    if (!fs.existsSync(filePath)) {
      console.log(`❌ 文件不存在: ${filePath}`);
      process.exit(1);
    }
    
    try {
      const fileContent = fs.readFileSync(filePath, 'utf8');
      let jobDataList;
      
      try {
        jobDataList = JSON.parse(fileContent);
      } catch (jsonError) {
        // 如果不是 JSON，当作每行一个查询
        jobDataList = fileContent.split('\n')
          .filter(line => line.trim().length > 0)
          .map(line => line.trim());
      }
      
      if (!Array.isArray(jobDataList)) {
        console.log('❌ 文件内容必须是数组或每行一个查询');
        process.exit(1);
      }
      
      console.log(`📦 加载 ${jobDataList.length} 个招聘数据`);
      const result = await this.processJobDataBatch(jobDataList, options);
      console.log(JSON.stringify(result, null, 2));
      
    } catch (error) {
      console.log(`❌ 处理文件失败: ${error.message}`);
      process.exit(1);
    }
  }
  
  /**
   * 处理 query 命令
   */
  async handleQueryCommand(args, options) {
    const query = args[0];
    
    if (!query) {
      console.log('❌ 需要提供查询词');
      process.exit(1);
    }
    
    const result = await this.queryJobHistory(query, options);
    console.log(JSON.stringify(result, null, 2));
  }
  
  /**
   * 处理 history 命令
   */
  async handleHistoryCommand(options) {
    try {
      // 查询最近的招聘
      const command = `${this.config.gbrainPath} query "招聘" --type job --limit 20`;
      const { stdout, stderr } = await execAsync(command, {
        env: {
          ...process.env,
          GBRAIN_HOME: this.config.gbrainHome
        },
        timeout: 30000
      });
      
      if (stderr && !stderr.includes('warning')) {
        throw new Error(`查询失败: ${stderr}`);
      }
      
      console.log('📋 最近的招聘历史:');
      console.log(stdout);
      
    } catch (error) {
      console.log(`❌ 查询历史失败: ${error.message}`);
      process.exit(1);
    }
  }
}

// 如果直接运行此文件
if (require.main === module) {
  const adapter = new JobToGBrainAdapter();
  adapter.runCLI().catch(error => {
    console.error('❌ 程序执行失败:', error);
    process.exit(1);
  });
}

module.exports = JobToGBrainAdapter;