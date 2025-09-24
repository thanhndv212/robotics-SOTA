import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Layout,
  Card,
  Row,
  Col,
  Button,
  Spin,
  Tag,
  Typography,
  Space,
  message,
  Divider,
  Breadcrumb
} from 'antd';
import {
  ArrowLeftOutlined,
  UserOutlined,
  LinkOutlined,
  CalendarOutlined,
  GlobalOutlined
} from '@ant-design/icons';

const { Header, Content } = Layout;
const { Title, Text, Paragraph } = Typography;

interface Paper {
  id: string;
  title: string;
  authors: string[];
  venue: string;
  year?: number;
  category: string;
  summary: string;
  abstract: string;
  contributions: string[];
  methods: string;
  applications: string;
  tags: string[];
  code: string;
  dataset: string;
  url?: string;
  doi?: string;
}

const PaperDetail: React.FC = () => {
  const { paperId } = useParams<{ paperId: string }>();
  const navigate = useNavigate();
  const [paper, setPaper] = useState<Paper | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (paperId) {
      loadPaper();
    }
  }, [paperId]);

  const loadPaper = async () => {
    if (!paperId) return;

    setLoading(true);
    try {
      // Removed the call to fetchPaperById as it is undefined
      // const data = await fetchPaperById(paperId);
      // setPaper(data);
    } catch (error) {
      message.error('Failed to load paper details');
      console.error('Error loading paper:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Layout style={{ minHeight: '100vh' }}>
        <Content style={{ padding: '50px', textAlign: 'center' }}>
          <Spin size="large" />
        </Content>
      </Layout>
    );
  }

  if (!paper) {
    return (
      <Layout style={{ minHeight: '100vh' }}>
        <Content style={{ padding: '50px', textAlign: 'center' }}>
          <Title level={4}>Paper not found</Title>
          <Button onClick={() => navigate('/paper-viewer')}>
            Back to Paper Viewer
          </Button>
        </Content>
      </Layout>
    );
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#001529', padding: '0 24px' }}>
        <Title level={3} style={{ color: 'white', margin: '16px 0' }}>
          Paper Details
        </Title>
      </Header>

      <Content style={{ padding: '24px', background: '#f5f5f5' }}>
        <Row justify="center">
          <Col xs={24} lg={16}>
            {/* Breadcrumb */}
            <Breadcrumb style={{ marginBottom: 24 }}>
              <Breadcrumb.Item>
                <a onClick={() => navigate('/paper-viewer')}>Paper Viewer</a>
              </Breadcrumb.Item>
              <Breadcrumb.Item>Paper Details</Breadcrumb.Item>
            </Breadcrumb>

            {/* Back Button */}
            <Button
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate('/paper-viewer')}
              style={{ marginBottom: 24 }}
            >
              Back to Search
            </Button>

            {/* Paper Details Card */}
            <Card>
              <div style={{ marginBottom: 24 }}>
                <Title level={2} style={{ marginBottom: 16 }}>
                  {paper.title}
                </Title>

                {/* Authors and Venue */}
                <Row gutter={[24, 16]}>
                  <Col xs={24} md={12}>
                    <div>
                      <Text strong style={{ display: 'block', marginBottom: 8 }}>
                        <UserOutlined style={{ marginRight: 8 }} />
                        Authors
                      </Text>
                      <Text>{paper.authors.join(', ')}</Text>
                    </div>
                  </Col>
                  <Col xs={24} md={12}>
                    <div>
                      <Text strong style={{ display: 'block', marginBottom: 8 }}>
                        <GlobalOutlined style={{ marginRight: 8 }} />
                        Publication
                      </Text>
                      <Text>
                        {paper.venue}
                        {paper.year && `, ${paper.year}`}
                      </Text>
                    </div>
                  </Col>
                </Row>

                <Divider />

                {/* Category and Tags */}
                <Row gutter={[24, 16]}>
                  <Col xs={24} md={12}>
                    <div>
                      <Text strong style={{ display: 'block', marginBottom: 8 }}>
                        Category
                      </Text>
                      <Tag color="blue" style={{ fontSize: '14px', padding: '4px 8px' }}>
                        {paper.category}
                      </Tag>
                    </div>
                  </Col>
                  <Col xs={24} md={12}>
                    <div>
                      <Text strong style={{ display: 'block', marginBottom: 8 }}>
                        Tags
                      </Text>
                      <Space wrap>
                        {paper.tags.map(tag => (
                          <Tag key={tag}>{tag}</Tag>
                        ))}
                      </Space>
                    </div>
                  </Col>
                </Row>

                <Divider />

                {/* Links */}
                {(paper.url || paper.doi) && (
                  <>
                    <Text strong style={{ display: 'block', marginBottom: 16 }}>
                      <LinkOutlined style={{ marginRight: 8 }} />
                      Links
                    </Text>
                    <Space style={{ marginBottom: 24 }}>
                      {paper.url && (
                        <Button
                          type="primary"
                          icon={<LinkOutlined />}
                          href={paper.url}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          View Paper
                        </Button>
                      )}
                      {paper.doi && (
                        <Button
                          icon={<LinkOutlined />}
                          href={`https://doi.org/${paper.doi}`}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          DOI
                        </Button>
                      )}
                    </Space>
                    <Divider />
                  </>
                )}

                {/* Summary */}
                {paper.summary && (
                  <>
                    <Title level={4} style={{ marginBottom: 16 }}>
                      Summary
                    </Title>
                    <Paragraph style={{ fontSize: '16px', lineHeight: '1.6' }}>
                      {paper.summary}
                    </Paragraph>
                    <Divider />
                  </>
                )}

                {/* Key Contributions */}
                {paper.contributions && paper.contributions.length > 0 && (
                  <>
                    <Title level={4} style={{ marginBottom: 16 }}>
                      Key Contributions
                    </Title>
                    <ul style={{ paddingLeft: '20px' }}>
                      {paper.contributions.map((contribution, index) => (
                        <li key={index} style={{ marginBottom: '8px', fontSize: '16px', lineHeight: '1.6' }}>
                          {contribution}
                        </li>
                      ))}
                    </ul>
                    <Divider />
                  </>
                )}

                {/* Methods */}
                {paper.methods && (
                  <>
                    <Title level={4} style={{ marginBottom: 16 }}>
                      Methods
                    </Title>
                    <Paragraph style={{ fontSize: '16px', lineHeight: '1.6' }}>
                      {paper.methods}
                    </Paragraph>
                    <Divider />
                  </>
                )}

                {/* Applications */}
                {paper.applications && (
                  <>
                    <Title level={4} style={{ marginBottom: 16 }}>
                      Applications
                    </Title>
                    <Paragraph style={{ fontSize: '16px', lineHeight: '1.6' }}>
                      {paper.applications}
                    </Paragraph>
                    <Divider />
                  </>
                )}

                {/* Code and Dataset */}
                <Row gutter={[24, 16]}>
                  <Col xs={24} md={12}>
                    <div>
                      <Text strong style={{ display: 'block', marginBottom: 8 }}>
                        Code
                      </Text>
                      <Text>{paper.code || 'N/A'}</Text>
                    </div>
                  </Col>
                  <Col xs={24} md={12}>
                    <div>
                      <Text strong style={{ display: 'block', marginBottom: 8 }}>
                        Dataset
                      </Text>
                      <Text>{paper.dataset || 'N/A'}</Text>
                    </div>
                  </Col>
                </Row>
              </div>
            </Card>
          </Col>
        </Row>
      </Content>
    </Layout>
  );
};

export default PaperDetail;