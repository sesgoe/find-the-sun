import * as pulumi from '@pulumi/pulumi';
import * as digitalocean from '@pulumi/digitalocean';
import * as kubernetes from '@pulumi/kubernetes';

const cfg = new pulumi.Config();

async function getKubernetesLatestVersion() {
    const versions = digitalocean.getKubernetesVersions({});
    return await (
        await versions
    ).latestVersion;
}

const cluster = new digitalocean.KubernetesCluster('find-the-sun-cluster', {
    region: digitalocean.Region.NYC1,
    version: getKubernetesLatestVersion(),
    nodePool: {
        name: 'default',
        size: digitalocean.DropletSlug.DropletS2VCPU2GB,
        nodeCount: 1,
    },
});

export const kubeconfig = cluster.kubeConfigs[0].rawConfig;

const provider = new kubernetes.Provider('find-the-sun-provider', { kubeconfig });

const appLabels = { app: 'app-find-the-sun' };
const app = new kubernetes.apps.v1.Deployment(
    'find-the-sun-deployment',
    {
        spec: {
            selector: { matchLabels: appLabels },
            replicas: 1,
            template: {
                metadata: { labels: appLabels },
                spec: {
                    containers: [
                        {
                            name: 'python-find-the-sun',
                            image: 'sesgoe/python-find-the-sun:v1.0.1',
                            env: [
                                {
                                    name: 'WEATHER_API_KEY',
                                    value: cfg.requireSecret('weatherapikey'),
                                },
                            ],
                            ports: [
                                {
                                    containerPort: 5000,
                                },
                            ],
                        },
                    ],
                },
            },
        },
    },
    { provider }
);

const appService = new kubernetes.core.v1.Service(
    'find-the-sun-service',
    {
        spec: {
            type: 'LoadBalancer',
            selector: app.spec.template.metadata.labels,
            ports: [{ port: 80, targetPort: 5000 }],
        },
    },
    { provider }
);

export const ingressIp = appService.status.loadBalancer.ingress[0].ip;
