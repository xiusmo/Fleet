<template>
  <div class="terms-page">
    <div class="terms-container">
      <div class="terms-header">
        <h1>服务条款</h1>
        <p class="last-updated">最后更新日期: 2025年3月30日</p>
      </div>

      <div class="terms-content">
        <section class="terms-section">
          <h2>1. 接受条款</h2>
          <p>欢迎使用学习痛签到助手（"服务"）。请仔细阅读以下条款和条件。通过访问或使用我们的服务，您同意受这些条款的约束。如果您不同意这些条款的任何部分，请不要使用我们的服务。</p>
        </section>

        <section class="terms-section">
          <h2>2. 服务描述</h2>
          <p>学习痛签到助手是一款帮助学生管理和自动化课程签到的工具。我们的服务旨在提高签到效率，但不保证所有签到都能成功完成。</p>
        </section>

        <section class="terms-section">
          <h2>3. 用户账户</h2>
          <p>使用我们的服务需要创建账户或使用现有的学习痛账户。您负责维护您账户的保密性，并对通过您的账户发生的所有活动负全责。</p>
        </section>

        <section class="terms-section">
          <h2>4. 用户行为</h2>
          <p>您同意不会：</p>
          <ul>
            <li>使用服务进行任何违法或未经授权的活动</li>
            <li>试图干扰或破坏服务的正常运行</li>
            <li>利用自动化手段进行未经授权的访问</li>
            <li>利用此服务<strong>代替他人签到</strong>或<strong>进行欺诈行为</strong></li>
          </ul>
        </section>

        <section class="terms-section">
          <h2>5. 数据使用</h2>
          <p>我们会收集必要的数据以提供服务。这包括您的账户信息和签到记录。但是您的密码<strong>不会</strong>被存储，我们不会泄露您的密码。我们不会收集除签到以外的任何数据。您同意我们可以根据我们的隐私政策处理这些数据。</p>
        </section>

        <section class="terms-section">
          <h2>6. 服务变更和终止</h2>
          <p>我们保留随时修改、暂停或终止服务的权利，恕不另行通知。我们也可能限制某些功能或限制您对部分或全部服务的访问。</p>
        </section>

        <section class="terms-section">
          <h2>7. 免责声明</h2>
          <p>服务"按原样"提供，不提供任何形式的保证。我们不保证服务将满足您的特定需求，或服务将不间断、及时、安全或无错误。</p>
        </section>

        <section class="terms-section">
          <h2>8. 责任限制</h2>
          <p>在法律允许的最大范围内，我们对任何直接、间接、附带、特殊、后果性或惩罚性损害不承担责任，包括因使用或无法使用服务而导致的损失。</p>
        </section>

        <section class="terms-section">
          <h2>9. 条款修改</h2>
          <p>我们可能会不时修改这些条款。修改后的条款将在我们的网站上发布时生效。您继续使用服务表示您接受修改后的条款。</p>
        </section>

        <section class="terms-section">
          <h2>10. 联系我们</h2>
          <p>如有任何问题或疑虑，请通过以下方式联系我们：xiusmo@gmail.com</p>
        </section>
      </div>

      <div class="terms-footer">
        <button class="btn btn-primary" @click="$router.go(-1)">返回</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TermsPage',
  mounted() {
    document.title = '服务条款'
  }
}
</script>

<style scoped>
.terms-page {
  padding: var(--spacing-4);
  min-height: 100vh;
  background-color: var(--color-bg);
}

.terms-container {
  max-width: 800px;
  margin: 0 auto;
  background-color: var(--color-card-bg);
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  padding: var(--spacing-4);
}

.terms-header {
  margin-bottom: var(--spacing-4);
  padding-bottom: var(--spacing-3);
  border-bottom: 1px solid var(--color-border);
}

.terms-header h1 {
  margin-bottom: var(--spacing-2);
  color: var(--color-primary);
}

.last-updated {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

.terms-content {
  margin-bottom: var(--spacing-4);
}

.terms-section {
  margin-bottom: var(--spacing-4);
}

.terms-section h2 {
  margin-bottom: var(--spacing-2);
  font-size: var(--font-size-lg);
  color: var(--color-text);
}

.terms-section p, .terms-section ul {
  margin-bottom: var(--spacing-2);
  line-height: 1.6;
  color: var(--color-text);
}

.terms-section ul {
  padding-left: var(--spacing-3);
}

.terms-section li {
  margin-bottom: var(--spacing-1);
}

.terms-footer {
  padding-top: var(--spacing-3);
  border-top: 1px solid var(--color-border);
  display: flex;
  justify-content: flex-end;
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .terms-container {
    border: 1px solid var(--color-border);
  }
}

.dark-mode .terms-container {
  border: 1px solid var(--color-border);
}
</style> 