/**
 * 本地数据备份模块
 * 负责本地数据备份的相关逻辑，包括保存、清除、清理等功能
 */

import { MAX_LOCAL_BACKUPS } from '../config/app-config.js';

/**
 * 本地备份处理器类
 */
export class TimeoutBackup {
  constructor() {
    // 备份键名前缀
    this.backupKeyPrefix = 'mcp_feedback_backup_';
  }

  /**
   * 保存反馈数据到本地存储 - P2.4 修复：增强本地备份功能的可靠性
   * @param {Object} data - 要保存的数据
   * @returns {string} 备份键名
   */
  saveToLocalBackup(data) {
    // 增加详细日志来调试存储过程

    // 检查 localStorage 是否可用
    if (typeof Storage === 'undefined') {
      throw new Error('浏览器不支持 localStorage');
    }

    // 检查存储空间
    const testKey = 'mcp_storage_test';
    try {
      localStorage.setItem(testKey, 'test');
      localStorage.removeItem(testKey);
    } catch (storageError) {
      throw new Error(`localStorage 不可用: ${storageError.message}`);
    }

    const backupKey = `${this.backupKeyPrefix}${Date.now()}`;
    const backupData = {
      ...data,
      backupTime: new Date().toISOString(),
      version: '1.0'
    };

    localStorage.setItem(backupKey, JSON.stringify(backupData));

    // 验证数据是否真的保存成功
    const savedData = localStorage.getItem(backupKey);
    if (!savedData) {
      throw new Error('数据保存后验证失败');
    }

    // 清理旧的备份数据（保留最近N个）
    this.cleanupOldBackups();

    return backupKey; // 返回备份键名以供后续使用
  }

  /**
   * 清除本地备份数据
   */
  clearLocalBackup() {
    try {
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.startsWith(this.backupKeyPrefix)) {
          localStorage.removeItem(key);
        }
      });
    } catch (error) {
    }
  }

  /**
   * 清理旧的备份数据，只保留最近的N个
   */
  cleanupOldBackups() {
    try {
      const keys = Object.keys(localStorage)
        .filter(key => key.startsWith(this.backupKeyPrefix))
        .sort((a, b) => {
          const timestampA = parseInt(a.split('_').pop());
          const timestampB = parseInt(b.split('_').pop());
          return timestampB - timestampA; // 降序排列
        });

      // 删除超过配置数量的旧备份
      if (keys.length > MAX_LOCAL_BACKUPS) {
        keys.slice(MAX_LOCAL_BACKUPS).forEach(key => {
          localStorage.removeItem(key);
        });
      }
    } catch (error) {
    }
  }

  /**
   * 获取所有本地备份数据
   * @returns {Array} 备份数据列表
   */
  getAllBackups() {
    try {
      const keys = Object.keys(localStorage)
        .filter(key => key.startsWith(this.backupKeyPrefix))
        .sort((a, b) => {
          const timestampA = parseInt(a.split('_').pop());
          const timestampB = parseInt(b.split('_').pop());
          return timestampB - timestampA; // 降序排列（最新的在前）
        });

      const backups = [];
      keys.forEach(key => {
        try {
          const data = JSON.parse(localStorage.getItem(key));
          backups.push({
            key,
            data,
            timestamp: data.backupTime || data.timestamp
          });
        } catch (parseError) {
        }
      });

      return backups;
    } catch (error) {
      return [];
    }
  }

  /**
   * 获取特定备份数据
   * @param {string} backupKey - 备份键名
   * @returns {Object|null} 备份数据或null
   */
  getBackup(backupKey) {
    try {
      const data = localStorage.getItem(backupKey);
      return data ? JSON.parse(data) : null;
    } catch (error) {
      return null;
    }
  }

  /**
   * 删除特定备份数据
   * @param {string} backupKey - 备份键名
   * @returns {boolean} 删除是否成功
   */
  removeBackup(backupKey) {
    try {
      localStorage.removeItem(backupKey);
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * 检查是否有本地备份数据
   * @returns {boolean} 是否有备份数据
   */
  hasBackups() {
    try {
      const keys = Object.keys(localStorage);
      return keys.some(key => key.startsWith(this.backupKeyPrefix));
    } catch (error) {
      return false;
    }
  }

  /**
   * 获取备份数据统计信息
   * @returns {Object} 统计信息
   */
  getBackupStats() {
    try {
      const backups = this.getAllBackups();
      let totalSize = 0;
      let textCount = 0;
      let imageCount = 0;

      backups.forEach(backup => {
        const data = backup.data;
        if (data.text && data.text.length > 0) {
          textCount++;
        }
        if (data.images && data.images.length > 0) {
          imageCount += data.images.length;
        }
        // 估算数据大小（字符串长度）
        totalSize += JSON.stringify(data).length;
      });

      return {
        count: backups.length,
        totalSize,
        textCount,
        imageCount,
        oldestBackup: backups.length > 0 ? backups[backups.length - 1].timestamp : null,
        newestBackup: backups.length > 0 ? backups[0].timestamp : null
      };
    } catch (error) {
      return {
        count: 0,
        totalSize: 0,
        textCount: 0,
        imageCount: 0,
        oldestBackup: null,
        newestBackup: null
      };
    }
  }
}
