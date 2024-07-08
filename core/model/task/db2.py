from datetime import date, datetime
from typing import Optional
from sqlalchemy import BIGINT, Column, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, aliased


class __Base(DeclarativeBase):
    pass


class MPLSTDB(__Base):
    __tablename__ = "LST"
    ID_LST: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    LST_ID_VLST: Mapped[int]
    LST_NAME: Mapped[str]
    LST_NAME_SH: Mapped[str]


class MPAppTaskDB(__Base):
    __tablename__: str = "APP_TASK"
    ID_APP_TASK: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    APP_TASK_ID_SOTR: Mapped[int] = mapped_column(BIGINT)
    APP_TASK_ID_APP_TASK: Mapped[int] = mapped_column(BIGINT, ForeignKey("APP_TASK.ID_APP_TASK"))
    APP_TASK_DT_START_PLN: Mapped[datetime]
    APP_TASK_DT_END_PLN: Mapped[datetime]
    APP_TASK_DT_START_FACT: Mapped[datetime | None]
    APP_TASK_DT_END_FACT: Mapped[datetime | None]
    APP_TASK_STATUS: Mapped[int]
    APP_TASK_TIP: Mapped[int]
    APP_TASK_TEXT: Mapped[str]
    APP_TASK_DEL: Mapped[int]

    subtasks: Mapped['MPAppTaskDB'] = relationship('MPAppTaskDB', remote_side=[ID_APP_TASK])


    @property
    def is_subtask(self) -> bool:
        return self.ID_APP_TASK != self.APP_TASK_ID_APP_TASK


class MPAppEventDB(__Base):
    __tablename__: str = "APP_EVENT"
    ID_APP_EVENT: Mapped[int]  = mapped_column(primary_key=True)
    APP_EVENT_ID_SOTR: Mapped[int]
    APP_EVENT_ID_REC: Mapped[int]
    APP_EVENT_VID: Mapped[int]
    APP_EVENT_TIP: Mapped[int]
    APP_EVENT_DT: Mapped[datetime | None]
    APP_EVENT_TEXT: Mapped[str | None]
    APP_EVENT_DATA: Mapped[str]
    APP_EVENT_DEL: Mapped[int]


class MPMSTDB(__Base):
    __tablename__ = "MST"
    ID_MST: Mapped[int] =  mapped_column(primary_key=True)
    MST_PR_OTHER: Mapped[int]
    MST_ID_KG: Mapped[int]
    MST_ID_SRV: Mapped[int]
    MST_ID_SETTLEMENT: Mapped[Optional[int]]
    MST_SID: Mapped[Optional[str]]
    MST_NAME: Mapped[Optional[str]]
    MST_CLI_NAME: Mapped[Optional[str]]
    MST_CODE: Mapped[int]
    MST_CODE_PODR_NDS: Mapped[int | None]
    MST_CODE_PODR_BN: Mapped[int | None]
    MST_PR_TTNINPUT: Mapped[int]
    MST_PR_TTNOUTPUT: Mapped[int]
    MST_PR_AEX: Mapped[int]
    MST_PR_AEX_ADR: Mapped[Optional[int]]
    MST_ID_MST_TTNOUTPUT: Mapped[int]
    MST_PR_SORT: Mapped[int]
    MST_PR_PVZ: Mapped[int]
    MST_PR_VIRT: Mapped[int]
    MST_PR_INOTHER: Mapped[int]
    MST_PR_ZAKG: Mapped[int]
    MST_PR_FAR: Mapped[int]
    MST_PR_KKT: Mapped[int]
    MST_PR_CC: Mapped[int]
    MST_PR_AS: Mapped[int]
    MST_KM: Mapped[int]
    MST_MP: Mapped[int]
    MST_ID_AGENT_AS: Mapped[int]
    MST_PR_NOLIM_AS: Mapped[int]
    MST_PR_WC_AS: Mapped[int]
    MST_PR_TRS: Mapped[int]
    MST_ID_REGION: Mapped[int]
    MST_ADDRESS_CODE: Mapped[int]
    MST_ID_KLADR_DOM: Mapped[Optional[int]]
    MST_SHIR: Mapped[float]
    MST_DOLG: Mapped[float]
    MST_ADR_STOR: Mapped[Optional[str]]
    MST_FUNC_MASK: Mapped[int]
    MST_ID_SRV_CALL: Mapped[int]
    MST_ID_MST_CALL: Mapped[int]
    MST_PR_DIRECT: Mapped[int]
    MST_NAME_DIRECT: Mapped[Optional[str]]
    MST_PR_NOTE: Mapped[int]
    MST_PR_NOTSITE: Mapped[int]
    MST_PR_GREEN: Mapped[int]
    MST_PR_GREENORK: Mapped[int]
    MST_PR_GREENPRINTER: Mapped[int]
    MST_PR_VID_TR_VD: Mapped[int]
    MST_PR_BAN_IN: Mapped[int]
    MST_PR_NO_CLIENT_CODES: Mapped[int]
    MST_PR_NO_STTN02: Mapped[int]
    MST_PR_NO_EEU: Mapped[int]
    MST_VID_CALC_FOBYOM: Mapped[int]
    MST_TXT: Mapped[Optional[str]]
    MST_DEL: Mapped[int]
    MST_CH: Mapped[Optional[datetime]]
    MST_WCH: Mapped[int]
    MST_IMP: Mapped[Optional[datetime]]
    MST_MPOST: Mapped[int]
    MST_SEANS: Mapped[int]
    MST_OWNERMST: Mapped[int]
    MST_CR: Mapped[Optional[datetime]]
    MST_WCR: Mapped[int]
    MST_FIMP: Mapped[Optional[datetime]]
    MST_ID_MST_SYNONYM: Mapped[int]
    MST_NAME_OLD: Mapped[Optional[str]]
    MST_SRC_OLD: Mapped[int]
    MST_UPPERNAME_OLD: Mapped[Optional[str]]
    MST_TXT_AEX: Mapped[Optional[str]]
    MST_PR_NODOOR_AEX: Mapped[int]


class MPTRSDB(__Base):
    __tablename__ = "TRS"
    ID_TRS: Mapped[int] = mapped_column(primary_key=True)
    TRS_PR_TEST: Mapped[int]
    TRS_PR_TEST_ID_SOTR: Mapped[int]
    TRS_PR_TEST_DT: Mapped[Optional[datetime]]
    TRS_PR: Mapped[int]
    TRS_PR_UP: Mapped[int]
    TRS_ID_LST_PR: Mapped[int]
    TRS_ID_LST_VID: Mapped[int]
    TRS_ID_LSTU_TIP: Mapped[int]
    TRS_SID: Mapped[Optional[str]]
    TRS_SID_GOST: Mapped[Optional[str]]
    TRS_SID_OLD: Mapped[Optional[str]]
    TRS_SRC_OLD: Mapped[int]
    TRS_PR_VLAD: Mapped[int]
    TRS_ID_AGENT_AS: Mapped[int]
    TRS_VES: Mapped[float]
    TRS_OBYOM: Mapped[float]
    TRS_PR_LTOR: Mapped[int]
    TRS_PR_LLEN: Mapped[int]
    TRS_PR_LTOP: Mapped[int]
    TRS_PR_TEPL: Mapped[int]
    TRS_PR_TEPL_WHERE: Mapped[int]
    TRS_OBYOM_TEPL: Mapped[float]
    TRS_PR_NOZAGRGRUZ: Mapped[int]
    TRS_CNT_AXIS: Mapped[int]
    TRS_PRIM: Mapped[Optional[str]]
    TRS_INFO: Mapped[Optional[str]]
    TRS_TARA: Mapped[Optional[float]]
    TRS_TYPEPROPERTY: Mapped[int]
    TRS_DOGAREND: Mapped[Optional[str]]
    TRS_1C_D_AKT: Mapped[Optional[date]]
    TRS_1C_NOMMSG: Mapped[int]
    TRS_1C_DEL: Mapped[int]
    TRS_1C_DATEEND: Mapped[Optional[date]]
    TRS_DEL: Mapped[int]
    TRS_CR: Mapped[Optional[datetime]]
    TRS_WCR: Mapped[int]
    TRS_CH: Mapped[Optional[datetime]]
    TRS_WCH: Mapped[int]
    TRS_OWNERMST: Mapped[int]
    TRS_SEANS: Mapped[int]
    TRS_IMP: Mapped[Optional[datetime]]
    TRS_FIMP: Mapped[Optional[datetime]]
    TRS_MPOST: Mapped[int]


class MPMarshDB(__Base):
    __tablename__ = "MARSH"
    ID_MARSH: Mapped[int] = mapped_column(primary_key=True)
    MARSH_PR: Mapped[int]
    MARSH_PR_PLAN: Mapped[int]
    MARSH_PR_VLAD: Mapped[int]
    MARSH_PR_DOP: Mapped[int]
    MARSH_PR_TEPL: Mapped[int]
    MARSH_KEY_GPREF: Mapped[Optional[str]]
    MARSH_KEY_PREF: Mapped[Optional[str]]
    MARSH_NAME: Mapped[Optional[str]]
    MARSH_D_N: Mapped[Optional[date]]
    MARSH_D_K: Mapped[Optional[date]]
    MARSH_ID_MST_OTPR: Mapped[int]
    MARSH_ID_MST_NAZN: Mapped[int]
    MARSH_DAYS_WEEK: Mapped[int]
    MARSH_T_OTPR: Mapped[float]
    MARSH_DATE_OUT: Mapped[Optional[date]]
    MARSH_PRICE: Mapped[Optional[float]]
    MARSH_KM: Mapped[Optional[float]]
    MARSH_TXT: Mapped[Optional[str]]
    MARSH_DEL: Mapped[int]


class MPMarshTRSDB(__Base):
    __tablename__ = "MARSH_TRS"
    ID_MARSH_TRS: Mapped[int] = mapped_column(primary_key=True)
    MARSH_TRS_ID_MARSH: Mapped[int]
    MARSH_TRS_DATE: Mapped[Optional[date]]
    MARSH_TRS_ID_TRS: Mapped[int]
    MARSH_TRS_TRS_PR_COLDONLY: Mapped[Optional[int]]
    MARSH_TRS_ID_PRIC: Mapped[int]
    MARSH_TRS_PRIC_PR_COLDONLY: Mapped[Optional[int]]
    MARSH_TRS_ID_SOTR: Mapped[int]
    MARSH_TRS_DT_DELIVERY: Mapped[Optional[datetime]]
    MARSH_TRS_PR: Mapped[int]
    MARSH_TRS_COMMENT: Mapped[Optional[str]]
    MARSH_TRS_TARIFF: Mapped[float]
    MARSH_TRS_DEL: Mapped[int]
    MARSH_TRS_OWNERMST: Mapped[int]
    MARSH_TRS_MPOST: Mapped[Optional[int]]
    MARSH_TRS_CR: Mapped[Optional[datetime]]
    MARSH_TRS_WCR: Mapped[int]
    MARSH_TRS_IMP: Mapped[Optional[datetime]]
    MARSH_TRS_CH: Mapped[Optional[datetime]]
    MARSH_TRS_WCH: Mapped[int]
    MARSH_TRS_SEANS: Mapped[int]
    MARSH_TRS_FIMP: Mapped[Optional[datetime]]


class MPAppParamDB(__Base):
    __tablename__ = "APP_PARAM"
    APP_PARAM_ID_REC: Mapped[int] = mapped_column(primary_key=True)
    APP_PARAM_STR: Mapped[Optional[str]]
    APP_PARAM_VID: Mapped[int]
    APP_PARAM_TIP: Mapped[int]
    APP_PARAM_DEL: Mapped[int]
    APP_PARAM_CR: Mapped[Optional[datetime]]
    APP_PARAM_WCR: Mapped[int]
    APP_PARAM_CH: Mapped[Optional[datetime]]
    APP_PARAM_WCH: Mapped[int]



# SET RELATIONS

