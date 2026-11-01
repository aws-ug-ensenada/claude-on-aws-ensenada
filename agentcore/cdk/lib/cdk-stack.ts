import { AgentCoreApplication, type AgentCoreApplicationProps } from '@aws/agentcore-cdk';
import { CfnResource, Stack, type StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface AgentCoreStackProps extends StackProps {
  /** Props for the AgentCore application, produced by transformAgentCoreJson from agentcore/agentcore.json. */
  application: AgentCoreApplicationProps;
}

/**
 * The stack the AgentCore CLI deploys. Everything declared in agentcore/agentcore.json is
 * created by the AgentCoreApplication construct. Add your own resources below it and wire
 * them to your runtimes and harnesses through the application's accessors.
 */
export class AgentCoreStack extends Stack {
  public readonly application: AgentCoreApplication;

  constructor(scope: Construct, id: string, props: AgentCoreStackProps) {
    super(scope, id, props);
    this.application = new AgentCoreApplication(this, 'Application', props.application);

    // Open-Meteo and Frankfurter need no key, but the CLI makes OpenAPI targets send one, as
    // `x-api-key`. Open-Meteo redirects any request with that header to its paid API, so the
    // placeholder key goes in a header both APIs ignore. Only the lunatools gateway's targets use the
    // placeholder; a target added elsewhere with a real key keeps the header its API expects.
    for (const node of this.node.findAll()) {
      if (
        node instanceof CfnResource &&
        node.cfnResourceType === 'AWS::BedrockAgentCore::GatewayTarget' &&
        /lunatools/i.test(node.node.path)
      ) {
        node.addPropertyOverride(
          'CredentialProviderConfigurations.0.CredentialProvider.ApiKeyCredentialProvider.CredentialParameterName',
          'X-Luna-Placeholder',
        );
      }
    }

    // Example: give a runtime a DynamoDB table.
    //
    // import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
    // const orders = new dynamodb.Table(this, 'Orders', {
    //   partitionKey: { name: 'pk', type: dynamodb.AttributeType.STRING },
    // });
    // const checkout = this.application.runtime('checkout'); // or .harness('support')
    // checkout.grantReadWrite(orders);
    // checkout.addEnvironmentVariable('ORDERS_TABLE', orders.tableName);
  }
}
