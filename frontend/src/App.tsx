import React, { useState, useEffect } from 'react';
import { Layout, Typography, Row, Col, Card, Alert, Input, Select, Pagination, Statistic, Tag, Space, Button } from 'antd';
import { SearchOutlined, GlobalOutlined, ExperimentOutlined } from '@ant-design/icons';
import './App.css';

const { Header, Content, Footer, Sider } = Layout;
const { Title, Paragraph } = Typography;
const { Option } = Select;

interface Lab {
  id: number;
  name: string;
  pi: string;
  institution: string;
  city: string;
  country: string;
  latitude: number;
  longitude: number;
  focus_areas: string[];
  website?: string;
}

const App: React.FC = () => {
  const [labs, setLabs] = useState<Lab[]>([]);
  const [filteredLabs, setFilteredLabs] = useState<Lab[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCountry, setSelectedCountry] = useState<string>('');
  const [selectedFocus, setSelectedFocus] = useState<string>('');
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedLab, setSelectedLab] = useState<Lab | null>(null);
  const pageSize = 12;

  useEffect(() => {
    const loadLabs = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://127.0.0.1:8080/api/labs/');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log('Loaded labs:', data.length);
        setLabs(data);
        setFilteredLabs(data);
        setError(null);
      } catch (err) {
        setError('Failed to load robotics labs data');
        console.error('Error loading labs:', err);
      } finally {
        setLoading(false);
      }
    };

    loadLabs();
  }, []);

  // Filter labs based on search criteria
  useEffect(() => {
    let filtered = labs;

    if (searchTerm) {
      filtered = filtered.filter(lab =>
        lab.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        lab.pi.toLowerCase().includes(searchTerm.toLowerCase()) ||
        lab.institution.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (selectedCountry) {
      filtered = filtered.filter(lab => lab.country === selectedCountry);
    }

    if (selectedFocus) {
      filtered = filtered.filter(lab => 
        lab.focus_areas && lab.focus_areas.some(area => 
          area.toLowerCase().includes(selectedFocus.toLowerCase())
        )
      );
    }

    setFilteredLabs(filtered);
    setCurrentPage(1);
  }, [searchTerm, selectedCountry, selectedFocus, labs]);

  // Get unique countries and focus areas for filters
  const countries = Array.from(new Set(labs.map(lab => lab.country))).sort();
  const allFocusAreas = labs.flatMap(lab => lab.focus_areas || []);
  const focusAreas = Array.from(new Set(allFocusAreas)).sort();

  // Get labs for current page
  const startIndex = (currentPage - 1) * pageSize;
  const currentLabs = filteredLabs.slice(startIndex, startIndex + pageSize);

  return (
    <Layout className="app-layout">
      <Header style={{ background: '#1890ff', padding: '0 24px' }}>
        <Title level={2} style={{ color: 'white', margin: 0, lineHeight: '64px' }}>
          🤖 Robotics Research Trends - State of the Art
        </Title>
      </Header>
      
      <Layout>
        <Sider width={300} style={{ background: '#fff', padding: '24px' }}>
          <Card title="Search & Filter" size="small">
            <Space direction="vertical" style={{ width: '100%' }}>
              <Input
                placeholder="Search labs, PIs, institutions..."
                prefix={<SearchOutlined />}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                allowClear
              />
              
              <Select
                placeholder="Filter by country"
                style={{ width: '100%' }}
                value={selectedCountry}
                onChange={setSelectedCountry}
                allowClear
              >
                {countries.map(country => (
                  <Option key={country} value={country}>{country}</Option>
                ))}
              </Select>
              
              <Select
                placeholder="Filter by focus area"
                style={{ width: '100%' }}
                value={selectedFocus}
                onChange={setSelectedFocus}
                allowClear
              >
                {focusAreas.slice(0, 20).map(focus => (
                  <Option key={focus} value={focus}>{focus}</Option>
                ))}
              </Select>
            </Space>
          </Card>

          <Card title="Statistics" style={{ marginTop: 16 }} size="small">
            <Row gutter={[8, 8]}>
              <Col span={12}>
                <Statistic 
                  title="Total Labs" 
                  value={labs.length} 
                  prefix={<GlobalOutlined />} 
                />
              </Col>
              <Col span={12}>
                <Statistic 
                  title="Countries" 
                  value={countries.length} 
                  prefix={<ExperimentOutlined />} 
                />
              </Col>
              <Col span={24}>
                <Statistic 
                  title="Filtered Results" 
                  value={filteredLabs.length} 
                  prefix={<SearchOutlined />} 
                />
              </Col>
            </Row>
          </Card>

          {selectedLab && (
            <Card title="Lab Details" style={{ marginTop: 16 }} size="small">
              <Title level={5}>{selectedLab.name}</Title>
              <p><strong>PI:</strong> {selectedLab.pi}</p>
              <p><strong>Institution:</strong> {selectedLab.institution}</p>
              <p><strong>Location:</strong> {selectedLab.city}, {selectedLab.country}</p>
              {selectedLab.focus_areas && selectedLab.focus_areas.length > 0 && (
                <div>
                  <p><strong>Focus Areas:</strong></p>
                  <div>
                    {selectedLab.focus_areas.map((area, index) => (
                      <Tag key={index} color="blue" style={{ marginBottom: 4 }}>
                        {area}
                      </Tag>
                    ))}
                  </div>
                </div>
              )}
              {selectedLab.website && (
                <Button 
                  type="primary" 
                  href={selectedLab.website} 
                  target="_blank"
                  style={{ marginTop: 8 }}
                >
                  Visit Website
                </Button>
              )}
            </Card>
          )}
        </Sider>

        <Content style={{ padding: '24px' }}>
          <Row gutter={[16, 16]}>
            <Col span={24}>
              <Card>
                <Title level={3}>Global Robotics Research Labs</Title>
                <Paragraph>
                  Interactive mapping of {labs.length} leading robotics research laboratories worldwide, 
                  tracking research trends, papers, and breakthrough technologies in robot learning, 
                  manipulation, perception, and autonomous systems.
                </Paragraph>
              </Card>
            </Col>
            
            <Col span={24}>
              <Card 
                title={`Research Labs (${filteredLabs.length} results)`} 
                loading={loading}
                extra={
                  <Pagination
                    current={currentPage}
                    total={filteredLabs.length}
                    pageSize={pageSize}
                    onChange={setCurrentPage}
                    showSizeChanger={false}
                    showQuickJumper
                    showTotal={(total, range) => 
                      `${range[0]}-${range[1]} of ${total} labs`
                    }
                  />
                }
              >
                {error ? (
                  <Alert message={error} type="error" />
                ) : (
                  <div>
                    <Row gutter={[16, 16]}>
                      {currentLabs.map((lab) => (
                        <Col span={8} key={lab.id}>
                          <Card 
                            size="small" 
                            title={lab.name.length > 35 ? lab.name.substring(0, 35) + '...' : lab.name}
                            style={{ 
                              height: '280px', 
                              cursor: 'pointer',
                              border: selectedLab?.id === lab.id ? '2px solid #1890ff' : undefined
                            }}
                            onClick={() => setSelectedLab(lab)}
                            hoverable
                          >
                            <p><strong>PI:</strong> {lab.pi}</p>
                            <p><strong>Institution:</strong> {
                              lab.institution.length > 30 ? 
                              lab.institution.substring(0, 30) + '...' : 
                              lab.institution
                            }</p>
                            <p><strong>Location:</strong> {lab.city}, {lab.country}</p>
                            
                            {lab.focus_areas && lab.focus_areas.length > 0 && (
                              <div style={{ marginTop: 8 }}>
                                <strong>Focus:</strong>
                                <div style={{ marginTop: 4 }}>
                                  {lab.focus_areas.slice(0, 2).map((area, index) => (
                                    <Tag key={index} color="geekblue">
                                      {area.length > 15 ? area.substring(0, 15) + '...' : area}
                                    </Tag>
                                  ))}
                                  {lab.focus_areas.length > 2 && (
                                    <Tag color="default">
                                      +{lab.focus_areas.length - 2}
                                    </Tag>
                                  )}
                                </div>
                              </div>
                            )}
                            
                            {lab.website && (
                              <Button 
                                type="link" 
                                size="small"
                                href={lab.website} 
                                target="_blank"
                                onClick={(e) => e.stopPropagation()}
                                style={{ padding: 0, marginTop: 8 }}
                              >
                                Visit Lab →
                              </Button>
                            )}
                          </Card>
                        </Col>
                      ))}
                    </Row>
                    
                    {filteredLabs.length === 0 && !loading && (
                      <div style={{ textAlign: 'center', padding: '40px' }}>
                        <Title level={4}>No labs found</Title>
                        <Paragraph>Try adjusting your search criteria</Paragraph>
                      </div>
                    )}
                  </div>
                )}
              </Card>
            </Col>
          </Row>
        </Content>
      </Layout>
      
      <Footer style={{ textAlign: 'center' }}>
        Robotics SOTA ©2025 - Interactive Research Trends Mapping
      </Footer>
    </Layout>
  );
};

export default App;