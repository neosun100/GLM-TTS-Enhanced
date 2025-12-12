# Swagger API 文档使用指南

## 📚 访问地址

**Swagger UI**: http://localhost:8080/apidocs/

**API规范**: http://localhost:8080/apispec_1.json

---

## ✨ 功能特点

### 1. 交互式文档
- ✅ 可视化API接口
- ✅ 在线测试功能
- ✅ 自动生成请求示例
- ✅ 实时查看响应结果

### 2. 完整的API覆盖

#### TTS相关
- `POST /api/tts` - 文本转语音（支持voice_id或上传音频）
- `POST /api/tts/with_voice` - 使用voice_id快速生成

#### 语音缓存管理
- `POST /api/voices` - 创建语音缓存
- `GET /api/voices` - 列出所有语音
- `GET /api/voices/{voice_id}` - 获取语音信息
- `DELETE /api/voices/{voice_id}` - 删除语音
- `GET /api/voices/{voice_id}/audio` - 下载参考音频

#### 系统信息
- `GET /api/cache/stats` - 缓存统计
- `GET /api/gpu/status` - GPU状态
- `POST /api/gpu/offload` - GPU卸载

---

## 🚀 使用方法

### 1. 打开Swagger UI

在浏览器中访问：
```
http://localhost:8080/apidocs/
```

### 2. 浏览API列表

页面会显示所有可用的API端点，按功能分组：
- **TTS** - 语音合成相关
- **Voice Cache** - 语音缓存管理
- **GPU** - GPU管理

### 3. 测试API

#### 步骤1：选择API端点
点击任意API端点展开详情

#### 步骤2：点击"Try it out"
启用交互式测试模式

#### 步骤3：填写参数
- 必填参数会标记为 `required`
- 可选参数可以留空
- 文件上传使用"Choose File"按钮

#### 步骤4：执行请求
点击"Execute"按钮发送请求

#### 步骤5：查看响应
- **Response body**: 返回的数据
- **Response headers**: HTTP头信息
- **Request URL**: 实际请求的URL
- **Curl**: 等效的curl命令

---

## 📖 API使用示例

### 示例1：创建语音缓存

1. 找到 `POST /api/voices`
2. 点击"Try it out"
3. 上传音频文件（audio参数）
4. 输入参考文本（prompt_text参数，可选）
5. 点击"Execute"
6. 查看返回的voice_id

**响应示例**：
```json
{
  "voice_id": "e2d8cdc3",
  "metadata": {
    "prompt_text": "这是我的声音",
    "created_at": "2025-12-12T15:00:00"
  }
}
```

### 示例2：使用voice_id生成TTS

1. 找到 `POST /api/tts`
2. 点击"Try it out"
3. 填写参数：
   - text: "你好，这是测试"
   - voice_id: "e2d8cdc3"
4. 点击"Execute"
5. 下载生成的音频文件

### 示例3：列出所有语音

1. 找到 `GET /api/voices`
2. 点击"Try it out"
3. 点击"Execute"
4. 查看所有缓存的语音列表

---

## 💡 高级功能

### 1. 导出为Curl命令

每次执行后，Swagger会显示等效的curl命令，可以直接复制使用：

```bash
curl -X POST "http://localhost:8080/api/tts" \
  -H "accept: audio/wav" \
  -H "Content-Type: multipart/form-data" \
  -F "text=你好" \
  -F "voice_id=e2d8cdc3"
```

### 2. 查看API规范

访问 http://localhost:8080/apispec_1.json 获取完整的OpenAPI规范（JSON格式）

可用于：
- 生成客户端SDK
- 导入到Postman
- 自动化测试
- API文档生成

### 3. 参数说明

每个参数都有详细说明：
- **类型**：string, number, file等
- **是否必需**：required或optional
- **默认值**：如果有
- **示例值**：参考示例
- **描述**：参数用途说明

---

## 🔧 集成到其他工具

### Postman集成

1. 打开Postman
2. 点击"Import"
3. 选择"Link"
4. 输入：`http://localhost:8080/apispec_1.json`
5. 点击"Import"

所有API会自动导入到Postman集合中。

### 代码生成

使用OpenAPI Generator生成客户端代码：

```bash
# 安装OpenAPI Generator
npm install @openapitools/openapi-generator-cli -g

# 生成Python客户端
openapi-generator-cli generate \
  -i http://localhost:8080/apispec_1.json \
  -g python \
  -o ./glm-tts-client

# 生成JavaScript客户端
openapi-generator-cli generate \
  -i http://localhost:8080/apispec_1.json \
  -g javascript \
  -o ./glm-tts-client-js
```

---

## 📱 移动端访问

Swagger UI是响应式的，可以在移动设备上访问：

1. 确保手机和服务器在同一网络
2. 使用服务器IP地址访问：
   ```
   http://服务器IP:8080/apidocs/
   ```
3. 可以直接在手机上测试API

---

## 🎯 最佳实践

### 1. 先测试后集成

在编写代码前，先在Swagger UI中测试API：
- 验证参数格式
- 查看响应结构
- 了解错误处理

### 2. 使用Curl命令

Swagger生成的curl命令可以直接用于：
- Shell脚本
- CI/CD流程
- 快速测试

### 3. 保存常用请求

在Swagger UI中测试成功后：
1. 复制curl命令
2. 保存到文档或脚本
3. 后续直接使用

---

## ❓ 常见问题

### Q1: Swagger UI无法访问？

**检查**：
```bash
# 检查服务是否运行
curl http://localhost:8080/health

# 检查端口是否开放
netstat -tuln | grep 8080
```

### Q2: 文件上传失败？

**原因**：文件太大或格式不支持

**解决**：
- 确保音频文件是WAV格式
- 文件大小<100MB
- 采样率24kHz或16kHz

### Q3: API返回404？

**原因**：端点路径错误

**解决**：
- 检查URL是否正确
- 确保使用正确的HTTP方法（GET/POST/DELETE）
- 查看Swagger文档中的完整路径

---

## 🔗 相关链接

- **Swagger官网**: https://swagger.io/
- **OpenAPI规范**: https://spec.openapis.org/oas/latest.html
- **Flasgger文档**: https://github.com/flasgger/flasgger

---

## 📊 API统计

当前版本（v1.1.0）提供的API端点：

| 分类 | 端点数 | 说明 |
|------|--------|------|
| TTS | 2 | 语音合成 |
| Voice Cache | 5 | 语音缓存管理 |
| System | 3 | 系统信息 |
| **总计** | **10** | **完整功能** |

---

**更新时间**: 2025-12-12  
**版本**: v1.1.0  
**Swagger UI**: ✅ 已启用
