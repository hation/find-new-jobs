#!/usr/bin/env node

/**
 * job-search GBrain 集成包装器
 * 增强招聘搜索功能，自动将搜索查询和职位信息保存到 GBrain
 */

const fs = require('fs');
const path = require('path');
const { exec, execSync } = require('child_process');
const { promisify } = require('util');

const execAsync = promisify(exec);

class JobSearchGBrain {
  constructor(configPath = null) {
    // 加载配置
    this.config = this.loadConfig(configPath);
    
    // 初始化适配器
    this.adapter = this.initAdapter();
    
    // 初始化日志
    this.initLogging();
    
    this.log('🚀 JobSearchGBrain 初始化完成', 'info');
  }
  
  /**
   * 加载配置
   */
  loadConfig(configPath) {
    const defaultConfig = {
      gbrain: {
        enabled: true,
        path: 'gbrain',
        home: path.join(process.env.HOME, '.gbrain'),
        autoSync: true,
        timeoutMs: 60000
      },
      jobSearch: {
        dataDir: path.join(process.env.HOME, '.openclaw/job-data'),
        cacheDir: path.join(process.env.HOME, '.openclaw/job-cache'),
        maxQueriesPerDay: 100,
        preserveOriginal: true
      },
      bossZhipin: {
        enabled: true,
        cliPath: '/Users/xingan/Library/Python/3.12/bin/boss',
        cookiePath: path.join(process.env.HOME, '.config/boss-cli/credential.json'),
        maxResultsPerQuery: 100,
        rateLimitMs: 2000
      },
      processing: {
        concurrent: 1,
        delayMs: 2000,
        retryAttempts: 3,
        validateBeforeSave: true
      },
      backup: {
        enabled: true,
        dir: path.join(process.env.HOME, '.openclaw/backup/job-search'),
        retentionDays: 180
      },
      logging: {
        enabled: true,
        level: 'info',
        dir: path.join(process.env.HOME, '.gbrain/logs/job-search'),
        maxFiles: 30
      }
    };
    
    // 尝试加载配置文件
    if (configPath && fs.existsSync(configPath)) {
      try {
        const customConfig = JSON.parse(fs.readFileSync(configPath, 'utf8'));
        return this.deepMerge(defaultConfig, customConfig);
      } catch (error) {
        this.log(`加载配置文件失败，使用默认配置: ${error.message}`, 'warn');
      }
    }
    
    // 尝试加载环境配置
    const envConfig = this.loadEnvConfig();
    if (envConfig) {
      return this.deepMerge(defaultConfig, envConfig);
    }
    
    return defaultConfig;
  }
  
  /**
   * 加载环境变量配置
   */
  loadEnvConfig() {
    const envConfig = {};
    
    if (process.env.GBRAIN_JOB_ENABLED) {
      envConfig.gbrain = envConfig.gbrain || {};
      envConfig.gbrain.enabled = process.env.GBRAIN_JOB_ENABLED === 'true';
    }
    
    if (process.env.JOB_DATA_DIR) {
      envConfig.jobSearch = envConfig.jobSearch || {};
      envConfig.jobSearch.dataDir = process.env.JOB_DATA_DIR;
    }
    
    if (process.env.JOB_CACHE_DIR) {
      envConfig.jobSearch = envConfig.jobSearch || {};
      envConfig.jobSearch.cacheDir = process.env.JOB_CACHE_DIR;
    }
    
    if (process.env.BOSS_CLI_PATH) {
      envConfig.bossZhipin = envConfig.bossZhipin || {};
      envConfig.bossZhipin.cliPath = process.env.BOSS_CLI_PATH;
    }
    
    return Object.keys(envConfig).length > 0 ? envConfig : null;
  }
  
  /**
   * 深度合并对象
   */
  deepMerge(target, source) {
    for (const key in source) {
      if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
        target[key] = this.deepMerge(target[key] || {}, source[key]);
      } else {
        target[key] = source[key];
      }
    }
    return target;
  }
  
  /**
   * 初始化适配器
   */
  initAdapter() {
    try {
      const adapterPath = path.join(__dirname, 'adapters/job-to-gbrain.js');
      if (fs.existsSync(adapterPath)) {
        const AdapterClass = require(adapterPath);
        return new AdapterClass({
          gbrainPath: this.config.gbrain.path,
          gbrainHome: this.config.gbrain.home,
          jobDataDir: this.config.jobSearch.dataDir,
          jobCacheDir: this.config.jobSearch.cacheDir,
          verbose: this.config.logging.level === 'debug'
        });
      } else {
        this.log(`适配器文件不存在: ${adapterPath}`, 'warn');
        return null;
      }
    } catch (error) {
      this.log(`初始化适配器失败: ${error.message}`, 'error');
      return null;
    }
  }
  
  /**
   * 初始化日志系统
   */
  initLogging() {
    if (!this.config.logging.enabled) return;
    
    const logDir = this.config.logging.dir;
    if (!fs.existsSync(logDir)) {
      fs.mkdirSync(logDir, { recursive: true });
    }
    
    this.logFile = path.join(logDir, `job-${new Date().toISOString().split('T')[0]}.log`);
  }
  
  /**
   * 日志记录
   */
  log(message, level = 'info') {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] [${level.toUpperCase()}] ${message}`;
    
    // 控制台输出
    if (this.config.logging.level === 'debug' || 
        (this.config.logging.level === 'info' && level !== 'debug') ||
        level === 'error' || level === 'warn') {
      const colors = {
        info: '\x1b[36m',
        debug: '\x1b[90m',
        warn: '\x1b[33m',
        error: '\x1b[31m',
        success: '\x1b[32m'
      };
      
      const reset = '\x1b[0m';
      const color = colors[level] || colors.info;
      
      if (level === 'success') {
        console.log(`✅ ${message}`);
      } else if (level === 'error') {
        console.error(`❌ ${message}`);
      } else if (level === 'warn') {
        console.warn(`⚠️  ${message}`);
      } else {
        console.log(`${color}${message}${reset}`);
      }
    }
    
    // 文件日志
    if (this.config.logging.enabled && this.logFile) {
      try {
        fs.appendFileSync(this.logFile, logMessage + '\n');
      } catch (error) {
        console.error(`日志文件写入失败: ${error.message}`);
      }
    }
  }
  
  /**
   * 检查依赖
   */
  async checkDependencies() {
    const checks = [
      {
        name: 'Node.js',
        check: async () => {
          const version = process.version;
          const major = parseInt(version.replace('v', '').split('.')[0]);
          return major >= 16;
        },
        message: '需要 Node.js 16+'
      },
      {
        name: 'GBrain',
        check: async () => {
          try {
            const { stdout } = await execAsync(`${this.config.gbrain.path} --version`);
            return stdout && stdout.trim().length > 0;
          } catch {
            return false;
          }
        },
        message: 'GBrain 未安装或不可用'
      },
      {
        name: 'boss-cli',
        check: async () => {
          if (!this.config.bossZhipin.enabled) {
            return true; // 如果未启用，跳过检查
          }
          
          try {
            const { stdout } = await execAsync(`${this.config.bossZhipin.cliPath} --version`);
            return stdout && stdout.trim().length > 0;
          } catch {
            return false;
          }
        },
        message: 'boss-cli 未安装或不可用'
      },
      {
        name: '招聘数据目录',
        check: async () => {
          try {
            const testFile = path.join(this.config.jobSearch.dataDir, '.test-permission');
            fs.writeFileSync(testFile, 'test');
            fs.unlinkSync(testFile);
            return true;
          } catch {
            return false;
          }
        },
        message: '招聘数据目录无写入权限'
      }
    ];
    
    this.log('🔍 检查系统依赖...', 'info');
    
    const results = [];
    for (const check of checks) {
      try {
        const passed = await check.check();
        results.push({
          name: check.name,
          passed,
          message: passed ? '✅ 通过' : `❌ ${check.message}`
        });
        
        this.log(`  ${passed ? '✅' : '❌'} ${check.name}: ${passed ? '通过' : check.message}`, 
                 passed ? 'info' : 'error');
      } catch (error) {
        results.push({
          name: check.name,
          passed: false,
          message: `❌ 检查失败: ${error.message}`
        });
        this.log(`  ❌ ${check.name}: 检查失败 - ${error.message}`, 'error');
      }
    }
    
    const allPassed = results.every(r => r.passed);
    if (!allPassed) {
      this.log('⚠️  部分依赖检查未通过，可能影响功能', 'warn');
    }
    
    return { allPassed, results };
  }
  
  /**
   * 处理招聘数据
   */
  async processJobData(jobData, options = {}) {
    try {
      this.log(`💼 处理招聘数据...`, 'info');
      
      if (!this.adapter) {
        throw new Error('适配器未初始化');
      }
      
      const result = await this.adapter.processJobData(jobData, options);
      
      if (result.success) {
        this.log(`✅ 招聘数据处理成功: ${result.jobData.jobName?.substring(0, 50) || result.jobData.query || result.jobData.id}`, 'success');
      } else {
        this.log(`❌ 招聘数据处理失败: ${result.error}`, 'error');
      }
      
      return result;
      
    } catch (error) {
      this.log(`❌ 处理招聘数据失败: ${error.message}`, 'error');
      throw error;
    }
  }
  
  /**
   * 执行招聘搜索并保存
   */
  async searchAndSave(query, options = {}) {
    try {
      this.log(`🔍 执行招聘搜索: "${query}"`, 'info');
      
      // 1. 执行招聘搜索（这里需要实际调用 boss-cli）
      const searchResult = await this.executeBossSearch(query, options);
      
      // 2. 处理招聘数据
      const processOptions = {
        ...options,
        source: 'boss-zhipin',
        searchTime: new Date().toISOString()
      };
      
      const processResult = await this.processJobData(searchResult, processOptions);
      
      // 3. 返回结果
      return {
        success: true,
        query: query,
        searchResult: searchResult,
        gbrainResult: processResult.gbrain,
        metadata: {
          processedAt: new Date().toISOString(),
          query: query,
          options: options
        }
      };
      
    } catch (error) {
      this.log(`❌ 招聘搜索并保存失败: ${error.message}`, 'error');
      throw error;
    }
  }
  
  /**
   * 执行 BOSS直聘搜索（模拟）
   */
  async executeBossSearch(query, options = {}) {
    // 这里应该调用实际的 boss-cli API
    // 目前使用模拟数据
    
    const searchId = `boss_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    return {
      id: searchId,
      query: query,
      results: this.generateMockJobResults(query, options),
      metadata: {
        source: 'boss-zhipin',
        city: options.city || '深圳',
        maxResults: options.maxResults || 10,
        searchTime: new Date().toISOString(),
        bossCli: this.config.bossZhipin.enabled ? '(已启用)' : '(未启用)'
      }
    };
  }
  
  /**
   * 生成模拟招聘结果
   */
  generateMockJobResults(query, options) {
    const companies = [
      '腾讯科技', '阿里巴巴', '字节跳动', '百度', '华为', '小米', '京东', '美团',
      '滴滴出行', '拼多多', '网易', '快手', '小红书', 'B站', '携程', '蔚来汽车'
    ];
    
    const jobTitles = [
      'AI开发工程师', '前端开发工程师', '后端开发工程师', '全栈工程师',
      '数据科学家', '机器学习工程师', '算法工程师', '产品经理',
      'UI设计师', '测试工程师', '运维工程师', 'DevOps工程师'
    ];
    
    const results = [];
    const count = options.maxResults || 10;
    
    for (let i = 0; i < count; i++) {
      const company = companies[i % companies.length];
      const jobTitle = jobTitles[i % jobTitles.length];
      const salary = `${15 + i * 2}-${25 + i * 3}K`;
      const experience = ['应届', '1-3年', '3-5年', '5-10年'][i % 4];
      const degree = ['大专', '本科', '硕士'][i % 3];
      
      results.push({
        jobName: `${jobTitle} - ${query}`,
        brandName: company,
        salaryDesc: salary,
        jobExperience: experience,
        jobDegree: degree,
        cityName: options.city || '深圳',
        brandScaleName: ['20-99人', '100-499人', '500-999人', '1000-9999人'][i % 4],
        brandIndustryName: '互联网',
        brandStageName: ['未融资', '天使轮', 'A轮', 'B轮', 'C轮', '已上市'][i % 6],
        jobDescription: `这是关于${jobTitle}的职位描述。职位要求包括${query}相关技能和经验。公司提供良好的发展空间和福利待遇。`,
        publishTime: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString()
      });
    }
    
    return results;
  }
  
  /**
   * 批量搜索并保存
   */
  async batchSearchAndSave(queries, options = {}) {
    const results = {
      total: queries.length,
      success: 0,
      failed: 0,
      details: []
    };
    
    this.log(`📦 批量执行 ${queries.length} 个招聘搜索`, 'info');
    
    for (let i = 0; i < queries.length; i++) {
      const query = queries[i];
      
      try {
        this.log(`🔍 执行搜索 ${i + 1}/${queries.length}: "${query}"`, 'info');
        
        const result = await this.searchAndSave(query, options);
        
        if (result.success) {
          results.success++;
          results.details.push({
            query: query,
            status: 'success',
            pageId: result.gbrainResult?.pageId,
            resultCount: result.searchResult?.results?.length,
            companyCount: new Set(result.searchResult?.results?.map(r => r.brandName)).size
          });
          
          this.log(`✅ 招聘搜索成功: "${query}"`, 'success');
        } else {
          results.failed++;
          results.details.push({
            query: query,
            status: 'failed',
            error: '处理失败'
          });
          
          this.log(`❌ 招聘搜索失败: "${query}"`, 'error');
        }
        
        // 延迟处理
        if (i < queries.length - 1 && this.config.processing.delayMs > 0) {
          await this.sleep(this.config.processing.delayMs);
        }
        
      } catch (error) {
        results.failed++;
        results.details.push({
          query: query,
          status: 'error',
          error: error.message
        });
        
        this.log(`❌ 招聘搜索异常: "${query}" - ${error.message}`, 'error');
      }
    }
    
    this.log(`📊 批量搜索完成: 成功 ${results.success}, 失败 ${results.failed}`, 'info');
    
    return results;
  }
  
  /**
   * 查询招聘历史
   */
  async queryJobHistory(query, options = {}) {
    if (!this.config.gbrain.enabled) {
      throw new Error('GBrain 集成未启用');
    }
    
    try {
      this.log(`🔍 查询招聘历史: "${query}"`, 'info');
      
      if (!this.adapter) {
        throw new Error('适配器未初始化');
      }
      
      const result = await this.adapter.queryJobHistory(query, options);
      
      if (result.success) {
        this.log(`✅ 查询完成: 找到 ${result.results.length} 个招聘记录`, 'success');
      } else {
        this.log(`❌ 查询失败`, 'error');
      }
      
      return result;
      
    } catch (error) {
      this.log(`❌ 查询失败: ${error.message}`, 'error');
      throw error;
    }
  }
  
  /**
   * 获取招聘统计
   */
  async getJobStats(options = {}) {
    try {
      this.log('📊 获取招聘统计...', 'info');
      
      // 查询招聘历史
      const historyResult = await this.queryJobHistory('', { limit: 1000 });
      
      if (!historyResult.success || historyResult.results.length === 0) {
        return {
          success: true,
          stats: {
            totalJobs: 0,
            recentSearches: [],
            topCompanies: [],
            topPositions: [],
            salaryDistribution: []
          }
        };
      }
      
      // 分析统计
      const stats = this.analyzeJobStats(historyResult.results, options);
      
      this.log(`✅ 统计完成: ${stats.totalJobs} 个招聘记录`, 'success');
      
      return {
        success: true,
        stats: stats
      };
      
    } catch (error) {
      this.log(`❌ 获取统计失败: ${error.message}`, 'error');
      throw error;
    }
  }
  
  /**
   * 分析招聘统计
   */
  analyzeJobStats(jobResults, options) {
    const stats = {
      totalJobs: jobResults.length,
      recentSearches: [],
      topCompanies: {},
      topPositions: {},
      salaryDistribution: {},
      byLocation: {},
      byExperience: {},
      byIndustry: {}
    };
    
    // 简单的统计逻辑
    // 实际实现需要从 GBrain 获取更多详细信息
    
    // 最近搜索
    stats.recentSearches = jobResults.slice(0, 10).map(r => r.title.replace('招聘搜索: ', ''));
    
    return stats;
  }
  
  /**
   * 生成招聘报告
   */
  async generateJobReport(options = {}) {
    try {
      this.log('📋 生成招聘报告...', 'info');
      
      const { period = 'week', limit = 100 } = options;
      
      // 1. 获取招聘统计
      const statsResult = await this.getJobStats(options);
      
      if (!statsResult.success) {
        throw new Error('获取统计失败');
      }
      
      // 2. 生成报告
      const report = this.generateReportContent(statsResult.stats, options);
      
      // 3. 保存到 GBrain（如果启用）
      let gbrainResult = null;
      if (this.config.gbrain.enabled) {
        gbrainResult = await this.saveReportToGBrain(report, options);
      }
      
      this.log(`✅ 招聘报告生成完成`, 'success');
      
      return {
        success: true,
        report: report,
        gbrain: gbrainResult,
        metadata: {
          generatedAt: new Date().toISOString(),
          period: period,
          jobCount: statsResult.stats.totalJobs,
          options: options
        }
      };
      
    } catch (error) {
      this.log(`❌ 生成招聘报告失败: ${error.message}`, 'error');
      throw error;
    }
  }
  
  /**
   * 生成报告内容
   */
  generateReportContent(stats, options) {
    const { period = 'week' } = options;
    
    const report = {
      title: `招聘分析报告 - ${period}`,
      generatedAt: new Date().toISOString(),
      stats: stats,
      summary: {
        totalJobs: stats.totalJobs,
        period: period,
        topCompany: Object.keys(stats.topCompanies)[0] || '无',
        topCompanyCount: stats.topCompanies[Object.keys(stats.topCompanies)[0]] || 0
      },
      insights: this.generateInsights(stats),
      recommendations: this.generateRecommendations(stats)
    };
    
    return report;
  }
  
  /**
   * 生成洞察
   */
  generateInsights(stats) {
    const insights = [];
    
    if (stats.totalJobs > 0) {
      insights.push({
        type: 'volume',
        message: `共收集 ${stats.totalJobs} 个招聘信息`,
        significance: 'high'
      });
    }
    
    if (Object.keys(stats.topCompanies).length > 0) {
      const topCompany = Object.keys(stats.topCompanies)[0];
      insights.push({
        type: 'popularity',
        message: `最热门的公司是"${topCompany}"，发布了 ${stats.topCompanies[topCompany]} 个职位`,
        significance: 'medium'
      });
    }
    
    if (stats.recentSearches.length > 0) {
      insights.push({
        type: 'recency',
        message: `最近搜索了: ${stats.recentSearches.slice(0, 3).join('、')}`,
        significance: 'low'
      });
    }
    
    return insights;
  }
  
  /**
   * 生成推荐
   */
  generateRecommendations(stats) {
    const recommendations = [];
    
    if (stats.totalJobs > 50) {
      recommendations.push({
        type: 'analysis',
        message: '招聘数据量较大，建议进行深度分析',
        action: '运行详细的分析报告'
      });
    }
    
    if (Object.keys(stats.topCompanies).length > 0 && stats.topCompanies[Object.keys(stats.topCompanies)[0]] > 10) {
      const topCompany = Object.keys(stats.topCompanies)[0];
      recommendations.push({
        type: 'focus',
        message: `"${topCompany}"发布了大量职位`,
        action: '针对该公司创建专门的关注列表'
      });
    }
    
    if (stats.totalJobs < 10) {
      recommendations.push({
        type: 'encouragement',
        message: '招聘数据较少',
        action: '增加更多招聘搜索'
      });
    }
    
    return recommendations;
  }
  
  /**
   * 保存报告到 GBrain
   */
  async saveReportToGBrain(report, options = {}) {
    try {
      if (!this.adapter) {
        throw new Error('适配器未初始化');
      }
      
      this.log('💾 保存报告到 GBrain...', 'info');
      
      // 构建报告招聘数据
      const reportJobData = {
        id: `report_${Date.now()}`,
        query: `招聘分析报告 - ${report.summary.period}`,
        source: 'job-analysis',
        parsedAt: new Date().toISOString(),
        summary: `招聘分析报告，包含 ${report.summary.totalJobs} 个招聘信息的分析结果`,
        content: this.formatReportForJobSearch(report),
        metadata: {
          type: 'report',
          period: report.summary.period,
          jobCount: report.summary.totalJobs,
          generatedAt: report.generatedAt
        }
      };
      
      // 保存到 GBrain
      const result = await this.adapter.saveJobToGBrain(reportJobData, options);
      
      this.log(`✅ 报告已保存到 GBrain: ${result.pageId}`, 'success');
      
      return result;
      
    } catch (error) {
      this.log(`❌ 保存报告到 GBrain 失败: ${error.message}`, 'error');
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  /**
   * 格式化报告为招聘数据
   */
  formatReportForJobSearch(report) {
    const sections = [];
    
    sections.push(`# ${report.title}`);
    sections.push('');
    sections.push(`生成时间: ${report.generatedAt}`);
    sections.push(`统计周期: ${report.summary.period}`);
    sections.push(`招聘总数: ${report.summary.totalJobs}`);
    sections.push(`最热公司: ${report.summary.topCompany} (${report.summary.topCompanyCount} 个职位)`);
    sections.push('');
    
    if (report.insights.length > 0) {
      sections.push('## 📊 关键洞察');
      sections.push('');
      report.insights.forEach(insight => {
        const emoji = insight.significance === 'high' ? '🔴' : 
                     insight.significance === 'medium' ? '🟡' : '🟢';
        sections.push(`${emoji} ${insight.message}`);
      });
      sections.push('');
    }
    
    if (report.recommendations.length > 0) {
      sections.push('## 🎯 行动建议');
      sections.push('');
      report.recommendations.forEach(rec => {
        sections.push(`- **${rec.message}**`);
        sections.push(`  建议: ${rec.action}`);
        sections.push('');
      });
    }
    
    if (Object.keys(report.stats.topCompanies).length > 0) {
      sections.push('## 🏢 热门公司');
      sections.push('');
      Object.entries(report.stats.topCompanies)
        .slice(0, 5)
        .forEach(([company, count], index) => {
          sections.push(`${index + 1}. **${company}** - ${count} 个职位`);
        });
      sections.push('');
    }
    
    if (report.stats.recentSearches.length > 0) {
      sections.push('## 🔍 最近搜索');
      sections.push('');
      report.stats.recentSearches.slice(0, 5).forEach((query, index) => {
        sections.push(`${index + 1}. ${query}`);
      });
      sections.push('');
    }
    
    return sections.join('\n');
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
      this.showHelp();
      return;
    }
    
    if (args.includes('--version') || args.includes('-v')) {
      console.log('job-search-gbrain v1.0.0');
      return;
    }
    
    // 解析命令
    const command = args[0];
    const commandArgs = args.slice(1);
    
    switch (command) {
      case 'search':
        await this.handleSearchCommand(commandArgs);
        break;
        
      case 'batch':
        await this.handleBatchCommand(commandArgs);
        break;
        
      case 'query':
        await this.handleQueryCommand(commandArgs);
        break;
        
      case 'stats':
        await this.handleStatsCommand(commandArgs);
        break;
        
      case 'report':
        await this.handleReportCommand(commandArgs);
        break;
        
      case 'check':
        await this.handleCheckCommand(commandArgs);
        break;
        
      case 'config':
        await this.handleConfigCommand(commandArgs);
        break;
        
      default:
        console.log(`❌ 未知命令: ${command}`);
        this.showHelp();
        process.exit(1);
    }
  }
  
  /**
   * 显示帮助
   */
  showHelp() {
    console.log(`
💼 job-search GBrain 集成工具

用法:
  node job-search-gbrain.js <命令> [参数]

命令:
  search <查询词>             执行招聘搜索并保存到 GBrain
  batch <文件>                批量执行招聘搜索
  query <搜索词>              查询招聘历史
  stats                      获取招聘统计
  report [选项]              生成招聘报告
  check                      检查系统状态
  config                     显示配置信息
  --help, -h                 显示帮助
  --version, -v              显示版本

示例:
  # 执行招聘搜索
  node job-search-gbrain.js search "AI开发工程师"
  
  # 批量搜索
  node job-search-gbrain.js batch queries.txt
  
  # 查询招聘历史
  node job-search-gbrain.js query "前端开发"
  
  # 获取统计
  node job-search-gbrain.js stats
  
  # 生成报告
  node job-search-gbrain.js report --period week

选项:
  --city <城市>              搜索城市（默认: 深圳）
  --max-results <数量>        最大结果数
  --period <周期>             报告周期 (day/week/month)
  --limit <数量>              限制数量
  --verbose                   详细输出
  --dry-run                   试运行，不保存

环境变量:
  GBRAIN_JOB_ENABLED         启用/禁用 GBrain 集成
  JOB_DATA_DIR               招聘数据目录
  JOB_CACHE_DIR              招聘缓存目录
  BOSS_CLI_PATH              boss-cli 路径
    `);
  }
  
  /**
   * 处理 search 命令
   */
  async handleSearchCommand(args) {
    const query = args.find(arg => !arg.startsWith('--'));
    
    if (!query) {
      console.log('❌ 需要提供搜索查询');
      process.exit(1);
    }
    
    const options = this.parseOptions(args);
    const result = await this.searchAndSave(query, options);
    console.log(JSON.stringify(result, null, 2));
  }
  
  /**
   * 处理 batch 命令
   */
  async handleBatchCommand(args) {
    const filePath = args.find(arg => !arg.startsWith('--'));
    
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
      const queries = fileContent.split('\n')
        .filter(line => line.trim().length > 0)
        .map(line => line.trim());
      
      if (queries.length === 0) {
        console.log('❌ 文件中没有查询词');
        process.exit(1);
      }
      
      console.log(`📦 加载 ${queries.length} 个查询词`);
      const options = this.parseOptions(args);
      const result = await this.batchSearchAndSave(queries, options);
      console.log(JSON.stringify(result, null, 2));
      
    } catch (error) {
      console.log(`❌ 处理文件失败: ${error.message}`);
      process.exit(1);
    }
  }
  
  /**
   * 处理 query 命令
   */
  async handleQueryCommand(args) {
    const query = args.find(arg => !arg.startsWith('--'));
    
    if (!query) {
      console.log('❌ 需要提供查询词');
      process.exit(1);
    }
    
    const options = this.parseOptions(args);
    const result = await this.queryJobHistory(query, options);
    console.log(JSON.stringify(result, null, 2));
  }
  
  /**
   * 处理 stats 命令
   */
  async handleStatsCommand(args) {
    const options = this.parseOptions(args);
    const result = await this.getJobStats(options);
    console.log(JSON.stringify(result, null, 2));
  }
  
  /**
   * 处理 report 命令
   */
  async handleReportCommand(args) {
    const options = this.parseOptions(args);
    const result = await this.generateJobReport(options);
    console.log(JSON.stringify(result, null, 2));
  }
  
  /**
   * 处理 check 命令
   */
  async handleCheckCommand(args) {
    const result = await this.checkDependencies();
    console.log(JSON.stringify(result, null, 2));
  }
  
  /**
   * 处理 config 命令
   */
  async handleConfigCommand(args) {
    console.log(JSON.stringify(this.config, null, 2));
  }
  
  /**
   * 解析命令行选项
   */
  parseOptions(args) {
    const options = {};
    
    for (let i = 0; i < args.length; i++) {
      const arg = args[i];
      
      if (arg === '--city') {
        options.city = args[++i];
      } else if (arg === '--max-results') {
        options.maxResults = parseInt(args[++i], 10);
      } else if (arg === '--period') {
        options.period = args[++i];
      } else if (arg === '--limit') {
        options.limit = parseInt(args[++i], 10);
      } else if (arg === '--verbose') {
        this.config.logging.level = 'debug';
      } else if (arg === '--dry-run') {
        options.dryRun = true;
      }
    }
    
    return options;
  }
}

// 如果直接运行此文件
if (require.main === module) {
  const configPath = process.env.CONFIG_PATH || 
    path.join(__dirname, 'config/gbrain-config.json');
  
  const app = new JobSearchGBrain(configPath);
  app.runCLI().catch(error => {
    console.error('❌ 程序执行失败:', error);
    process.exit(1);
  });
}

module.exports = JobSearchGBrain;