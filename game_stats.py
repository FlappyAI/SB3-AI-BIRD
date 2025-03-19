import json
import os

class GameStats:
    def __init__(self):
        self.stats_file = 'game_stats.json'
        self.stats = self.load_stats()

    def load_stats(self):
        """加载游戏统计数据"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            except:
                return self.get_default_stats()
        return self.get_default_stats()

    def save_stats(self):
        """保存游戏统计数据"""
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f)

    def get_default_stats(self):
        """获取默认统计数据"""
        return {
            'death_count': 0,
            'high_score': 0,
            'max_frame': 0
        }

    def update_death_count(self, count):
        """更新死亡次数"""
        self.stats['death_count'] = count
        self.save_stats()

    def update_high_score(self, score):
        """更新最高分"""
        if score > self.stats['high_score']:
            self.stats['high_score'] = score
            self.save_stats()

    def update_max_frame(self, frame):
        """更新最大帧数"""
        if frame > self.stats['max_frame']:
            self.stats['max_frame'] = frame
            self.save_stats()

    def get_death_count(self):
        """获取死亡次数"""
        return self.stats['death_count']

    def get_high_score(self):
        """获取最高分"""
        return self.stats['high_score']

    def get_max_frame(self):
        """获取最大帧数"""
        return self.stats['max_frame'] 