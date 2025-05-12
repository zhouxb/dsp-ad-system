from typing import Dict, List, Optional, Any
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Table, Text, Enum, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import JSON

from app.models.base import BaseModel, AuditLogMixin, db


class Advertiser(BaseModel, AuditLogMixin):
    """Advertiser model representing advertising client"""
    __tablename__ = 'advertiser'

    name = Column(String(100), nullable=False, comment='广告主名称')
    company_name = Column(String(200), nullable=False, comment='公司名称')
    credit_code = Column(String(50), comment='营业执照统一社会信用代码')
    contact_person = Column(String(50), nullable=False, comment='联系人')
    contact_phone = Column(String(20), nullable=False, comment='联系电话')
    contact_email = Column(String(100), nullable=False, comment='联系邮箱')
    address = Column(String(255), comment='公司地址')
    status = Column(Enum('pending', 'approved', 'rejected', 'suspended'), nullable=False, default='pending', comment='状态')
    balance = Column(Float, nullable=False, default=0, comment='账户余额')
    qualification_docs = Column(JSON, default=lambda: [], comment='资质文件URL列表')
    rejection_reason = Column(Text, comment='拒绝原因')
    review_history = Column(JSON, default=lambda: [], comment='审核历史')
    account_manager_id = Column(Integer, ForeignKey('user.id', name='fk_advertiser_account_manager_id'), comment='账户经理ID')
    
    # Business category and industry
    industry = Column(String(50), comment='所属行业')
    business_type = Column(String(50), comment='业务类型')
    
    # Settings and configuration
    settings = Column(JSON, default=lambda: {}, comment='广告主设置')
    
    # Relationships
    users = relationship("User", back_populates="advertiser", foreign_keys="User.advertiser_id")
    campaigns = relationship("Campaign", back_populates="advertiser")
    qualification_files = relationship("QualificationFile", back_populates="advertiser")
    account_manager = relationship("User", back_populates="managed_advertisers", foreign_keys=[account_manager_id])
    creatives = relationship("Creative", back_populates="advertiser")
    transactions = relationship("Transaction", back_populates="advertiser")
    
    def __repr__(self) -> str:
        return f"<Advertiser {self.name}>"
    
    def add_document(self, document_url: str, document_type: str, uploaded_by: int) -> None:
        """Add a qualification document to the advertiser"""
        if not self.qualification_docs:
            self.qualification_docs = []
            
        doc = {
            "url": document_url,
            "type": document_type,
            "uploaded_at": db.func.now(),
            "uploaded_by": uploaded_by
        }
        
        self.qualification_docs.append(doc)
    
    def set_status(self, status: str, reviewed_by: int, reason: str = None) -> None:
        """Update advertiser status and add to review history"""
        old_status = self.status
        self.status = status
        
        if not self.review_history:
            self.review_history = []
            
        review_entry = {
            "from_status": old_status,
            "to_status": status,
            "reviewed_by": reviewed_by,
            "reviewed_at": db.func.now(),
            "reason": reason
        }
        
        self.review_history.append(review_entry)
        
        if status == 'rejected' and reason:
            self.rejection_reason = reason
            
    def deposit(self, amount: float, transaction_id: str, deposited_by: int) -> float:
        """Add funds to advertiser account"""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
            
        self.balance += amount
        
        # Log the transaction
        transaction = Transaction(
            advertiser_id=self.id,
            amount=amount,
            balance_after=self.balance,
            transaction_type="deposit",
            reference_id=transaction_id,
            created_by_id=deposited_by
        )
        transaction.save()
        
        return self.balance
        
    def withdraw(self, amount: float, transaction_id: str, withdrawn_by: int) -> float:
        """Withdraw funds from advertiser account"""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
            
        if amount > self.balance:
            raise ValueError("Insufficient funds for withdrawal")
            
        self.balance -= amount
        
        # Log the transaction
        transaction = Transaction(
            advertiser_id=self.id,
            amount=-amount,
            balance_after=self.balance,
            transaction_type="withdrawal",
            reference_id=transaction_id,
            created_by_id=withdrawn_by
        )
        transaction.save()
        
        return self.balance


class QualificationFile(BaseModel, AuditLogMixin):
    """Model for advertiser qualification files"""
    __tablename__ = 'qualification_file'

    advertiser_id = Column(Integer, ForeignKey('advertiser.id', name='fk_qualification_file_advertiser_id'), nullable=False, comment='广告主ID')
    file_path = Column(String(255), nullable=False, comment='文件路径')
    file_type = Column(String(50), nullable=False, comment='文件类型')
    file_size = Column(Integer, nullable=False, comment='文件大小(字节)')
    original_name = Column(String(255), nullable=False, comment='原始文件名')
    status = Column(Enum('pending', 'approved', 'rejected'), nullable=False, default='pending', comment='状态')
    uploaded_by_id = Column(Integer, ForeignKey('user.id', name='fk_qualification_file_uploaded_by_id'), nullable=False, comment='上传人ID')
    reviewed_by_id = Column(Integer, ForeignKey('user.id', name='fk_qualification_file_reviewed_by_id'), comment='审核人ID')
    review_time = Column(DateTime, comment='审核时间')
    review_comment = Column(Text, comment='审核意见')
    
    # Relationships
    advertiser = relationship("Advertiser", back_populates="qualification_files")
    uploaded_by = relationship("User", foreign_keys=[uploaded_by_id])
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_id])
    
    def __repr__(self) -> str:
        return f"<QualificationFile {self.original_name}>"
    
    def approve(self, reviewed_by_id: int, comment: str = None) -> None:
        """Approve the qualification file"""
        self.status = 'approved'
        self.reviewed_by_id = reviewed_by_id
        if comment:
            self.review_comment = comment
            
    def reject(self, reviewed_by_id: int, comment: str) -> None:
        """Reject the qualification file"""
        self.status = 'rejected'
        self.reviewed_by_id = reviewed_by_id
        self.review_comment = comment


class Transaction(BaseModel, AuditLogMixin):
    """Model for financial transactions"""
    __tablename__ = 'transaction'

    advertiser_id = Column(Integer, ForeignKey('advertiser.id', name='fk_transaction_advertiser_id'), nullable=False, comment='广告主ID')
    amount = Column(Float, nullable=False, comment='交易金额')
    balance_after = Column(Float, nullable=False, comment='交易后余额')
    transaction_type = Column(Enum('deposit', 'withdraw', 'spend', 'refund'), nullable=False, comment='交易类型')
    reference_id = Column(String(50), nullable=False, unique=True, comment='交易参考号')
    status = Column(Enum('pending', 'completed', 'failed'), nullable=False, default='pending', comment='交易状态')
    payment_method = Column(String(50), comment='支付方式')
    payment_account = Column(String(100), comment='支付账号')
    created_by_id = Column(Integer, ForeignKey('user.id', name='fk_transaction_created_by_id'), nullable=False, comment='创建人ID')
    completed_at = Column(DateTime, comment='完成时间')
    failure_reason = Column(Text, comment='失败原因')
    
    # Relationships
    advertiser = relationship("Advertiser", back_populates="transactions")
    created_by = relationship("User", foreign_keys=[created_by_id])
    
    def __repr__(self) -> str:
        return f"<Transaction {self.reference_id}>" 