// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// Licensed under the 【火山方舟】原型应用软件自用许可协议
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at 
//     https://www.volcengine.com/docs/82379/1433703
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package config

type MobileUseConfig struct {
	// 这里用匿名嵌入把三个小结构拼成一个总配置，
	// 调用方既可以整体传 MobileUseConfig，也可以直接通过字段名读取子配置。
	AuthInfo
	BizInfo
	TosInfo
}

type AuthInfo struct {
	// CurrentTime / ExpiredTime 主要用于临时凭证场景，
	// AccessKeyId / SecretAccessKey / SessionToken 才是访问云接口的核心身份信息。
	CurrentTime     string
	ExpiredTime     string
	AccessKeyId     string
	SecretAccessKey string
	SessionToken    string
}

type BizInfo struct {
	// 这些字段描述“要操作哪一台云手机”。
	ACEPHost  string
	ProductId string
	DeviceId  string
}

type TosInfo struct {
	// 截图会上传到 TOS，因此这里保存和对象存储相关的访问参数。
	TosBucket       string
	TosRegion       string
	TosEndpoint     string
	TosAccessKey    string
	TosSecretKey    string
	TosSessionToken string
}
