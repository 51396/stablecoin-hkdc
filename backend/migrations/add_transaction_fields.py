"""
添加交易字段的数据库迁移脚本
"""

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base


def upgrade(engine):
    """
    添加新的交易字段
    """
    # 添加字段到Transaction表
    with engine.connect() as conn:
        # 添加发起方地址字段
        conn.execute("ALTER TABLE transactions ADD COLUMN from_address VARCHAR(42) NULL")
        
        # 添加接收方地址字段
        conn.execute("ALTER TABLE transactions ADD COLUMN to_address VARCHAR(42) NULL")
        
        # 添加gas使用量字段
        conn.execute("ALTER TABLE transactions ADD COLUMN gas_used INTEGER NULL")
        
        # 添加gas价格字段
        conn.execute("ALTER TABLE transactions ADD COLUMN gas_price VARCHAR(20) NULL")
        
        # 添加手续费字段
        conn.execute("ALTER TABLE transactions ADD COLUMN fee FLOAT NULL")
        
        conn.commit()


def downgrade(engine):
    """
    回滚添加的交易字段
    """
    # 从Transaction表中删除字段
    with engine.connect() as conn:
        # 删除手续费字段
        conn.execute("ALTER TABLE transactions DROP COLUMN fee")
        
        # 删除gas价格字段
        conn.execute("ALTER TABLE transactions DROP COLUMN gas_price")
        
        # 删除gas使用量字段
        conn.execute("ALTER TABLE transactions DROP COLUMN gas_used")
        
        # 删除接收方地址字段
        conn.execute("ALTER TABLE transactions DROP COLUMN to_address")
        
        # 删除发起方地址字段
        conn.execute("ALTER TABLE transactions DROP COLUMN from_address")
        
        conn.commit()