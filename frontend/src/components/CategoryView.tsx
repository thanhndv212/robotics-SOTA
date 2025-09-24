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
  Breadcrumb,
  Statistic,
  List
} from 'antd';
import {
  ArrowLeftOutlined,
  FileTextOutlined,
  UserOutlined,
  CalendarOutlined
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
  tags: string[];
  url?: string;
}

const CategoryView: React.FC = () => {
  const { categoryName } = useParams<{ categoryName: string }>();
  const navigate = useNavigate();
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState('');
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (categoryName) {
      loadCategoryPapers();
    }
  }, [categoryName]);

  const loadCategoryPapers = async () => {
    if (!categoryName) return;

    setLoading(true);
    try {
      const response = await fetch(
        `https://api.example.com/papers?category=${categoryName}`
      );
      const data = await response.json();
      setPapers(data.papers || []);
      setCategory(data.category || categoryName);
      setCount(data.count || 0);
    } catch (error) {
      message.error('Failed to load category papers');
      console.error('Error loading category papers:', error);
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

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#001529', padding: '0 24px' }}>
        <Title level={3} style={{ color: 'white', margin: '16px 0' }}>
          <FileTextOutlined style={{ marginRight: 8 }} />
          Paper Viewer
        </Title>
      </Header>

      <Content style={{ padding: '24px', background: '#f5f5f5' }}>
        <Row justify="center">
          <Col xs={24} lg={20}>
            {/* Breadcrumb */}
            <Breadcrumb style={{ marginBottom: 24 }}>
              <Breadcrumb.Item>
                <a onClick={() => navigate('/paper-viewer')}>Paper Viewer</a>
              </Breadcrumb.Item>
              <Breadcrumb.Item>{category}</Breadcrumb.Item>
            </Breadcrumb>

            {/* Back Button */}
            <Button
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate('/paper-viewer')}
              style={{ marginBottom: 24 }}
            >
              Back to Search
            </Button>

            {/* Category Header */}
            <Card style={{ marginBottom: 24 }}>
              <Row align="middle" justify="space-between">
                <Col>
                  <Title level={2} style={{ marginBottom: 8 }}>
                    {category}
                  </Title>
                  <Text type="secondary">
                    Browse papers in this category
                  </Text>
                </Col>
                <Col>
                  <Statistic
                    title="Total Papers"
                    value={count}
                    valueStyle={{ color: '#1890ff' }}
                  />
                </Col>
              </Row>
            </Card>

            {/* Papers List */}
            <Card>
              <List
                dataSource={papers}
                renderItem={(paper) => (
                  <List.Item>
                    <Card
                      hoverable
                      style={{ width: '100%', marginBottom: 16 }}
                      onClick={() => navigate(`/paper-viewer/paper/${paper.id}`)}
                    >
                      <Row>
                        <Col xs={24} md={20}>
                          <Title level={5}>
                            {paper.url ? (
                              <a
                                href={paper.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                onClick={(e) => e.stopPropagation()}
                              >
                                {paper.title}
                              </a>
                            ) : (
                              paper.title
                            )}
                          </Title>
                          <Space style={{ marginBottom: 8 }}>
                            <UserOutlined />
                            <Text>{paper.authors.join(', ')}</Text>
                          </Space>
                          <Space style={{ marginBottom: 8 }}>
                            <Text type="secondary">
                              {paper.venue}{paper.year ? `, ${paper.year}` : ''}
                            </Text>
                          </Space>
                          <Paragraph ellipsis={{ rows: 2 }}>
                            {paper.summary}
                          </Paragraph>
                          <div>
                            {paper.tags.map(tag => (
                              <Tag key={tag} style={{ marginBottom: 4 }}>
                                {tag}
                              </Tag>
                            ))}
                          </div>
                        </Col>
                        <Col xs={24} md={4} style={{ textAlign: 'right' }}>
                          <Tag color="blue">{paper.category}</Tag>
                          <br />
                          <Button
                            type="link"
                            style={{ padding: 0, marginTop: 8 }}
                            onClick={(e) => {
                              e.stopPropagation();
                              navigate(`/paper-viewer/paper/${paper.id}`);
                            }}
                          >
                            View Details →
                          </Button>
                        </Col>
                      </Row>
                    </Card>
                  </List.Item>
                )}
              />
            </Card>
          </Col>
        </Row>
      </Content>
    </Layout>
  );
};

export default CategoryView;