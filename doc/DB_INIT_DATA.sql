-- ================================================================================
--                    ERP 系統資料庫初始資料腳本
--                    Database: SQL Server
--                    Version: 1.0
-- ================================================================================
-- 使用方式：
-- 1. 先執行所有 migration SQL 檔案建立資料表結構
-- 2. 再執行此腳本插入初始資料
-- ================================================================================

-- ================================================================================
-- 【第一部分】系統參數設定 (parameter)
-- ================================================================================
-- 此表儲存系統的基本參數設定

INSERT INTO [dbo].[parameter] ([name], [value]) VALUES
-- 客戶編號設定
(N'CustomerIDCharacter', N''),              -- 客戶編號起始字母（空=純數字，A=台北市，依城市設定）
(N'CustomerIDLength', N'6'),                -- 客戶編號長度
(N'CustomerIDAreaLength', N'4'),            -- 地區客戶編號長度

-- 廠商編號設定
(N'ManufacturerIDLength', N'4'),            -- 廠商編號長度

-- 訂單設定
(N'OrderNumberLength', N'8'),               -- 訂單號長度

-- 票據設定
(N'InitialCheckNumber', N'1'),              -- 票據起始號
(N'NowCheckNumber', N'1'),                  -- 目前票據流水號

-- 其他設定
(N'DefaultShippingFee', N'0'),              -- 預設運費
(N'ExportCompanyFormat', N''),              -- 匯出公司格式
(N'ProjectCodeDefaultUrl', N''),            -- 專案編號預設網址

-- API 服務設定
(N'APIServiceEnabled', N'false'),           -- API服務啟用
(N'APIServicePort', N'8080'),               -- API服務連接埠
(N'APIServiceContextPath', N'/api');        -- API服務上下文路徑
GO

-- ================================================================================
-- 【第二部分】系統預設配置 (SystemDefaultConfig)
-- ================================================================================
-- 此表儲存系統功能的開關設定（1=啟用，0=停用）

INSERT INTO [dbo].[SystemDefaultConfig] ([config_name], [default_value]) VALUES
(N'UploadPictureFunction', 1),                              -- 上傳圖片功能
(N'Order_SnapshotCamera', 1),                               -- 訂單快照攝影機
(N'Order_DefaultProductConnection', 0),                     -- 訂單預設商品連接
(N'Order_SearchFunction', 0),                               -- 訂單搜尋功能
(N'Order_PrintFunction', 1),                                -- 訂單列印功能
(N'Order_ExportPurchaseFunction', 1),                       -- 訂單匯出採購功能
(N'Order_ExportPayReceiveDetails', 0),                      -- 訂單匯出應收應付詳情
(N'WaitingConfirm_DefaultSearchProductNameFunction', 1),    -- 待確認預設搜尋商品名稱
(N'SearchOrder_DefaultSearchTextFunction', 1);              -- 搜尋訂單預設文本搜尋
GO

-- ================================================================================
-- 【第三部分】維修狀態 (repair_status)
-- ================================================================================
-- 維修單的狀態選項

INSERT INTO [dbo].[repair_status] ([name]) VALUES
(N'待處理'),
(N'處理中'),
(N'已完成'),
(N'已取消'),
(N'待取件'),
(N'已寄回');
GO

-- ================================================================================
-- 【第四部分】銀行資訊 (Bank)
-- ================================================================================
-- 常用銀行代碼與名稱

INSERT INTO [dbo].[Bank] ([BankCode], [BankNickName], [BankName], [ContactPerson1], [ContactPerson2], [Telephone1], [Telephone2], [Fax], [Address], [Remark]) VALUES
(N'004', N'台銀', N'臺灣銀行', N'', N'', N'', N'', N'', N'', N''),
(N'005', N'土銀', N'臺灣土地銀行', N'', N'', N'', N'', N'', N'', N''),
(N'006', N'合庫', N'合作金庫商業銀行', N'', N'', N'', N'', N'', N'', N''),
(N'007', N'一銀', N'第一商業銀行', N'', N'', N'', N'', N'', N'', N''),
(N'008', N'華銀', N'華南商業銀行', N'', N'', N'', N'', N'', N'', N''),
(N'009', N'彰銀', N'彰化商業銀行', N'', N'', N'', N'', N'', N'', N''),
(N'011', N'上海', N'上海商業儲蓄銀行', N'', N'', N'', N'', N'', N'', N''),
(N'012', N'台北富邦', N'台北富邦商業銀行', N'', N'', N'', N'', N'', N'', N''),
(N'013', N'國泰世華', N'國泰世華商業銀行', N'', N'', N'', N'', N'', N'', N''),
(N'017', N'兆豐', N'兆豐國際商業銀行', N'', N'', N'', N'', N'', N'', N''),
(N'021', N'花旗', N'花旗(台灣)商業銀行', N'', N'', N'', N'', N'', N'', N''),
(N'048', N'王道', N'王道商業銀行', N'', N'', N'', N'', N'', N'', N''),
(N'050', N'臺企銀', N'臺灣中小企業銀行', N'', N'', N'', N'', N'', N'', N''),
(N'052', N'渣打', N'渣打國際商業銀行', N'', N'', N'', N'', N'', N'', N''),
(N'053', N'台中銀', N'台中商業銀行', N'', N'', N'', N'', N'', N'', N''),
(N'081', N'匯豐', N'匯豐(台灣)商業銀行', N'', N'', N'', N'', N'', N'', N''),
(N'101', N'瑞興', N'瑞興商業銀行', N'', N'', N'', N'', N'', N'', N''),
(N'102', N'華泰', N'華泰商業銀行', N'', N'', N'', N'', N'', N'', N''),
(N'103', N'新光', N'臺灣新光商業銀行', N'', N'', N'', N'', N'', N'', N''),
(N'108', N'陽信', N'陽信商業銀行', N'', N'', N'', N'', N'', N'', N''),
(N'118', N'板信', N'板信商業銀行', N'', N'', N'', N'', N'', N'', N''),
(N'147', N'三信', N'三信商業銀行', N'', N'', N'', N'', N'', N'', N''),
(N'700', N'中華郵政', N'中華郵政', N'', N'', N'', N'', N'', N'', N''),
(N'803', N'聯邦', N'聯邦商業銀行', N'', N'', N'', N'', N'', N'', N''),
(N'805', N'遠東', N'遠東國際商業銀行', N'', N'', N'', N'', N'', N'', N''),
(N'806', N'元大', N'元大商業銀行', N'', N'', N'', N'', N'', N'', N''),
(N'807', N'永豐', N'永豐商業銀行', N'', N'', N'', N'', N'', N'', N''),
(N'808', N'玉山', N'玉山商業銀行', N'', N'', N'', N'', N'', N'', N''),
(N'809', N'凱基', N'凱基商業銀行', N'', N'', N'', N'', N'', N'', N''),
(N'810', N'星展', N'星展(台灣)商業銀行', N'', N'', N'', N'', N'', N'', N''),
(N'812', N'台新', N'台新國際商業銀行', N'', N'', N'', N'', N'', N'', N''),
(N'816', N'安泰', N'安泰商業銀行', N'', N'', N'', N'', N'', N'', N''),
(N'822', N'中信', N'中國信託商業銀行', N'', N'', N'', N'', N'', N'', N''),
(N'824', N'連線', N'連線商業銀行', N'', N'', N'', N'', N'', N'', N'');
GO

-- ================================================================================
-- 【第五部分】供應商分類 - 建達國際 (category_xander)
-- ================================================================================
-- 供應商代碼：778

INSERT INTO [dbo].[category_xander] ([Category], [Name], [Value], [Layer], [LastUpdate_Category], [Exist]) VALUES
-- 大類別 (Layer = 1)
(NULL, N'電腦周邊', N'peripheral', N'1', 0, 1),
(NULL, N'網路通訊', N'network', N'1', 0, 1),
(NULL, N'儲存設備', N'storage', N'1', 0, 1),
(NULL, N'電腦零組件', N'components', N'1', 0, 1),
(NULL, N'辦公設備', N'office', N'1', 0, 1),
(NULL, N'消費電子', N'consumer', N'1', 0, 1),

-- 中類別 (Layer = 2)
(N'peripheral', N'鍵盤滑鼠', N'keyboard_mouse', N'2', 0, 1),
(N'peripheral', N'耳機喇叭', N'audio', N'2', 0, 1),
(N'peripheral', N'視訊設備', N'video', N'2', 0, 1),
(N'network', N'路由器', N'router', N'2', 0, 1),
(N'network', N'網路卡', N'network_card', N'2', 0, 1),
(N'storage', N'隨身碟', N'usb_drive', N'2', 0, 1),
(N'storage', N'硬碟', N'hdd', N'2', 0, 1),

-- 小類別 (Layer = 3)
(N'keyboard_mouse', N'有線滑鼠', N'wired_mouse', N'3', 0, 1),
(N'keyboard_mouse', N'無線滑鼠', N'wireless_mouse', N'3', 0, 1),
(N'keyboard_mouse', N'有線鍵盤', N'wired_keyboard', N'3', 0, 1),
(N'keyboard_mouse', N'無線鍵盤', N'wireless_keyboard', N'3', 0, 1),
(N'audio', N'有線耳機', N'wired_headset', N'3', 0, 1),
(N'audio', N'無線耳機', N'wireless_headset', N'3', 0, 1),
(N'audio', N'喇叭', N'speaker', N'3', 0, 1);
GO

-- ================================================================================
-- 【第六部分】供應商分類 - 廣鐸企業 (category_ktnet)
-- ================================================================================
-- 供應商代碼：750

INSERT INTO [dbo].[category_ktnet] ([Category], [Name], [Value], [Layer], [LastUpdate_Category], [Exist]) VALUES
-- 大類別 (Layer = 1)
(NULL, N'電腦周邊', N'peripheral', N'1', 0, 1),
(NULL, N'網路設備', N'network', N'1', 0, 1),
(NULL, N'消費電子', N'consumer', N'1', 0, 1),

-- 中類別 (Layer = 2)
(N'peripheral', N'鍵盤滑鼠', N'keyboard_mouse', N'2', 0, 1),
(N'peripheral', N'USB周邊', N'usb', N'2', 0, 1),
(N'network', N'網路線材', N'cable', N'2', 0, 1),

-- 小類別 (Layer = 3)
(N'keyboard_mouse', N'有線滑鼠', N'wired_mouse', N'3', 0, 1),
(N'keyboard_mouse', N'有線鍵盤', N'wired_keyboard', N'3', 0, 1);
GO

-- ================================================================================
-- 【第七部分】供應商分類 - Genuine捷元 (category_genb2b)
-- ================================================================================
-- 供應商代碼：779

INSERT INTO [dbo].[category_genb2b] ([Category], [Name], [Value], [Layer], [LastUpdate_Category], [Exist]) VALUES
-- 大類別 (Layer = 1)
(NULL, N'電腦系統', N'system', N'1', 0, 1),
(NULL, N'電腦零組件', N'components', N'1', 0, 1),
(NULL, N'周邊設備', N'peripheral', N'1', 0, 1),
(NULL, N'軟體', N'software', N'1', 0, 1),

-- 中類別 (Layer = 2)
(N'system', N'桌上型電腦', N'desktop', N'2', 0, 1),
(N'system', N'筆記型電腦', N'notebook', N'2', 0, 1),
(N'components', N'主機板', N'motherboard', N'2', 0, 1),
(N'components', N'顯示卡', N'vga', N'2', 0, 1),
(N'components', N'記憶體', N'memory', N'2', 0, 1);
GO

-- ================================================================================
-- 【第八部分】供應商分類 - 聯強國際 (category_synnex)
-- ================================================================================
-- 供應商代碼：777

INSERT INTO [dbo].[category_synnex] ([Category], [Name], [Value], [Layer], [LastUpdate_Category], [Exist]) VALUES
-- 大類別 (Layer = 1)
(NULL, N'電腦系統', N'system', N'1', 0, 1),
(NULL, N'零組件', N'components', N'1', 0, 1),
(NULL, N'周邊產品', N'peripheral', N'1', 0, 1),
(NULL, N'消費性電子', N'consumer', N'1', 0, 1),

-- 中類別 (Layer = 2)
(N'system', N'桌機', N'desktop', N'2', 0, 1),
(N'system', N'筆電', N'notebook', N'2', 0, 1),
(N'components', N'CPU', N'cpu', N'2', 0, 1),
(N'components', N'主機板', N'motherboard', N'2', 0, 1),
(N'peripheral', N'顯示器', N'monitor', N'2', 0, 1),
(N'peripheral', N'印表機', N'printer', N'2', 0, 1);
GO

-- ================================================================================
-- 【第九部分】供應商分類 - 精技電腦 (category_unitech)
-- ================================================================================
-- 供應商代碼：776

INSERT INTO [dbo].[category_unitech] ([Category], [Name], [Value], [Layer], [LastUpdate_Category], [Exist]) VALUES
-- 大類別 (Layer = 1)
(NULL, N'電腦周邊', N'peripheral', N'1', 0, 1),
(NULL, N'網通產品', N'network', N'1', 0, 1),
(NULL, N'消費電子', N'consumer', N'1', 0, 1),

-- 中類別 (Layer = 2)
(N'peripheral', N'輸入裝置', N'input', N'2', 0, 1),
(N'peripheral', N'儲存裝置', N'storage', N'2', 0, 1),
(N'network', N'無線網路', N'wireless', N'2', 0, 1);
GO

-- ================================================================================
-- 【第十部分】供應商分類 - 展碁國際 (category_weblink)
-- ================================================================================
-- 供應商代碼：781

INSERT INTO [dbo].[category_weblink] ([Category], [Name], [Value], [Layer], [LastUpdate_Category], [Exist]) VALUES
-- 大類別 (Layer = 1)
(NULL, N'電腦周邊', N'peripheral', N'1', 0, 1),
(NULL, N'網路通訊', N'network', N'1', 0, 1),
(NULL, N'數位產品', N'digital', N'1', 0, 1),

-- 中類別 (Layer = 2)
(N'peripheral', N'鍵盤滑鼠', N'keyboard_mouse', N'2', 0, 1),
(N'peripheral', N'音訊設備', N'audio', N'2', 0, 1),
(N'network', N'路由器', N'router', N'2', 0, 1);
GO

-- ================================================================================
-- 【第十一部分】供應商分類 - 神腦國際 (category_senao)
-- ================================================================================
-- 供應商代碼：787

INSERT INTO [dbo].[category_senao] ([Category], [Name], [Value], [Layer], [LastUpdate_Category], [Exist]) VALUES
-- 大類別 (Layer = 1)
(NULL, N'手機通訊', N'mobile', N'1', 0, 1),
(NULL, N'電腦周邊', N'peripheral', N'1', 0, 1),
(NULL, N'消費電子', N'consumer', N'1', 0, 1),

-- 中類別 (Layer = 2)
(N'mobile', N'智慧型手機', N'smartphone', N'2', 0, 1),
(N'mobile', N'手機配件', N'accessory', N'2', 0, 1),
(N'peripheral', N'耳機', N'headset', N'2', 0, 1);
GO

-- ================================================================================
-- 【第十二部分】供應商分類 - 精豪電腦 (category_jinghao)
-- ================================================================================
-- 供應商代碼：780

INSERT INTO [dbo].[category_jinghao] ([Category], [Name], [Value], [Layer], [LastUpdate_Category], [Exist]) VALUES
-- 大類別 (Layer = 1)
(NULL, N'電腦周邊', N'peripheral', N'1', 0, 1),
(NULL, N'網路設備', N'network', N'1', 0, 1),

-- 中類別 (Layer = 2)
(N'peripheral', N'鍵盤滑鼠', N'keyboard_mouse', N'2', 0, 1),
(N'peripheral', N'USB產品', N'usb', N'2', 0, 1),
(N'network', N'網路線材', N'cable', N'2', 0, 1);
GO

-- ================================================================================
-- 【第十三部分】貨架位置 (BookCase) - 選填
-- ================================================================================
-- 可依實際倉庫配置調整

INSERT INTO [dbo].[BookCase] ([ProductArea], [ProductFloor], [Level]) VALUES
(N'A區', N'1層', 1),
(N'A區', N'2層', 2),
(N'A區', N'3層', 3),
(N'B區', N'1層', 1),
(N'B區', N'2層', 2),
(N'B區', N'3層', 3),
(N'C區', N'1層', 1),
(N'C區', N'2層', 2),
(N'C區', N'3層', 3);
GO

-- ================================================================================
--                              初始化完成
-- ================================================================================
--
-- 供應商代碼對照表：
-- ┌──────┬────────────┬─────────────────────┐
-- │ 代碼 │  英文名    │      中文名         │
-- ├──────┼────────────┼─────────────────────┤
-- │ 778  │ Xander     │ 建達國際            │
-- │ 750  │ Ktnet      │ 廣鐸企業            │
-- │ 779  │ Genb2b     │ Genuine捷元         │
-- │ 777  │ Synnex     │ 聯強國際            │
-- │ 776  │ Unitech    │ 精技電腦            │
-- │ 781  │ Weblink    │ 展碁國際            │
-- │ 787  │ Senao      │ 神腦國際            │
-- │ 780  │ Jinghao    │ 精豪電腦            │
-- └──────┴────────────┴─────────────────────┘
--
-- 注意事項：
-- 1. 供應商分類資料為範例，請依實際需求調整
-- 2. 分類的 Value 欄位需與供應商系統對應
-- 3. Layer: 1=大類別, 2=中類別, 3=小類別
-- 4. 中類別的 Category 欄位需對應大類別的 Value
-- 5. 小類別的 Category 欄位需對應中類別的 Value
--
-- ================================================================================
