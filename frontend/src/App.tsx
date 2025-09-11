import React, { useState, useEffect } from 'react';
import { Layout, Typography, Row, Col, Card, Alert, Input, Select, Pagination, Statistic, Tag, Space, Button, Modal, Checkbox, Divider, Tooltip, Avatar, List, Dropdown, Popconfirm, message } from 'antd';
import { SearchOutlined, GlobalOutlined, ExperimentOutlined, FileTextOutlined, DownloadOutlined, LinkOutlined, ExpandAltOutlined, CompressOutlined, CalendarOutlined, TeamOutlined, DollarOutlined, PlusOutlined, EditOutlined, DeleteOutlined, MoreOutlined } from '@ant-design/icons';
import LabFormModal from './components/LabFormModal';
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
  description?: string;
  established_year?: number;
  funding_sources?: string[];
  papers?: Paper[];
  paper_count?: number;
}

interface Paper {
  id: number;
  title: string;
  authors: string;
  abstract?: string;
  publication_date?: string;
  venue?: string;
  paper_type?: string;
  arxiv_id?: string;
  doi?: string;
  pdf_url?: string;
  website_url?: string;
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
  const [expandedLabId, setExpandedLabId] = useState<number | null>(null);
  const [scrapeModalVisible, setScrapeModalVisible] = useState(false);
  const [selectedLabsForScraping, setSelectedLabsForScraping] = useState<number[]>([]);
  const [scrapingSources, setScrapingSources] = useState<string[]>(['arxiv']);
  const [scrapingInProgress, setScrapingInProgress] = useState(false);
  const [labFormVisible, setLabFormVisible] = useState(false);
  const [currentLab, setCurrentLab] = useState<Lab | null>(null);
  const [formMode, setFormMode] = useState<'create' | 'edit'>('create');
  const pageSize = 12;

  useEffect(() => {
    const loadLabs = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://127.0.0.1:8080/api/labs/?include_papers=true');
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

  const handleScrapePapers = async () => {
    try {
      setScrapingInProgress(true);
      const response = await fetch('http://127.0.0.1:8080/api/labs/scrape-papers', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          lab_ids: selectedLabsForScraping,
          sources: scrapingSources,
          max_papers: 5
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('Scraping result:', result);
        
        // Reload labs data to show new papers
        const labsResponse = await fetch('http://127.0.0.1:8080/api/labs/?include_papers=true');
        if (labsResponse.ok) {
          const updatedLabs = await labsResponse.json();
          setLabs(updatedLabs);
          setFilteredLabs(updatedLabs);
        }
        
        setScrapeModalVisible(false);
        setSelectedLabsForScraping([]);
      } else {
        console.error('Scraping failed:', response.statusText);
      }
    } catch (error) {
      console.error('Error during scraping:', error);
    } finally {
      setScrapingInProgress(false);
    }
  };

  const handleCreateLab = () => {
    setCurrentLab(null);
    setFormMode('create');
    setLabFormVisible(true);
  };

  const handleEditLab = (lab: Lab) => {
    setCurrentLab(lab);
    setFormMode('edit');
    setLabFormVisible(true);
  };

  const handleDeleteLab = async (labId: number) => {
    try {
      const response = await fetch(`http://127.0.0.1:8080/api/labs/${labId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        message.success('Lab deleted successfully!');
        // Refresh the labs list
        const labsResponse = await fetch('http://127.0.0.1:8080/api/labs/?include_papers=true');
        if (labsResponse.ok) {
          const updatedLabs = await labsResponse.json();
          setLabs(updatedLabs);
          setFilteredLabs(updatedLabs);
        }
      } else {
        const error = await response.json();
        message.error(error.error || 'Delete failed');
      }
    } catch (error) {
      message.error('Network error occurred');
      console.error('Delete error:', error);
    }
  };

  const handleLabFormSuccess = async () => {
    // Refresh the labs list
    try {
      const response = await fetch('http://127.0.0.1:8080/api/labs/?include_papers=true');
      if (response.ok) {
        const updatedLabs = await response.json();
        setLabs(updatedLabs);
        setFilteredLabs(updatedLabs);
      }
    } catch (error) {
      console.error('Error refreshing labs:', error);
    }
    setLabFormVisible(false);
  };

  const getLabActions = (lab: Lab) => [
    {
      key: 'edit',
      label: 'Edit Lab',
      icon: <EditOutlined />,
      onClick: () => handleEditLab(lab),
    },
    {
      key: 'delete',
      label: 'Delete Lab',
      icon: <DeleteOutlined />,
      danger: true,
      onClick: () => {
        Modal.confirm({
          title: 'Delete Lab',
          content: `Are you sure you want to delete "${lab.name}"? This action cannot be undone.`,
          okText: 'Yes, Delete',
          okType: 'danger',
          cancelText: 'Cancel',
          onOk: () => handleDeleteLab(lab.id!),
        });
      },
    },
  ];

  const handleCardClick = (lab: Lab) => {
    if (expandedLabId === lab.id) {
      setExpandedLabId(null);
      setSelectedLab(null);
    } else {
      setExpandedLabId(lab.id);
      setSelectedLab(lab);
    }
  };

  const formatAuthors = (authorsString: string) => {
    try {
      const authors = JSON.parse(authorsString);
      if (Array.isArray(authors)) {
        return authors.slice(0, 3).join(', ') + (authors.length > 3 ? ' et al.' : '');
      }
      return authorsString;
    } catch {
      return authorsString.split(',').slice(0, 3).join(', ') + (authorsString.split(',').length > 3 ? ' et al.' : '');
    }
  };

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
            <Header style={{ background: '#001529', padding: '0 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Title level={2} style={{ color: 'white', margin: 0 }}>
          🤖 Robotics Research Trends - State of the Art
        </Title>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={handleCreateLab}
          size="large"
          style={{ backgroundColor: '#52c41a', borderColor: '#52c41a' }}
        >
          Add New Lab
        </Button>
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
                  prefix={<GlobalOutlined />} 
                />
              </Col>
              <Col span={12}>
                <Statistic 
                  title="Papers" 
                  value={labs.reduce((sum, lab) => sum + (lab.paper_count || 0), 0)} 
                  prefix={<FileTextOutlined />} 
                />
              </Col>
              <Col span={12}>
                <Statistic 
                  title="With Papers" 
                  value={labs.filter(lab => (lab.paper_count || 0) > 0).length} 
                  prefix={<ExperimentOutlined />} 
                />
              </Col>
            </Row>
            
            <Button 
              type="primary" 
              block 
              style={{ marginTop: 16 }}
              onClick={() => setScrapeModalVisible(true)}
              icon={<DownloadOutlined />}
            >
              Scrape Latest Papers
            </Button>
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
                      {currentLabs.map((lab) => {
                        const isExpanded = expandedLabId === lab.id;
                        return (
                          <Col span={isExpanded ? 24 : 8} key={lab.id}>
                            <Card 
                              size="small" 
                              className={`lab-card ${isExpanded ? 'expanded' : ''}`}
                              title={
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                    <Avatar style={{ backgroundColor: '#1890ff' }}>
                                      {lab.name.charAt(0)}
                                    </Avatar>
                                    <span style={{ fontSize: isExpanded ? '18px' : '14px', fontWeight: 'bold' }}>
                                      {isExpanded ? lab.name : (lab.name.length > 30 ? lab.name.substring(0, 30) + '...' : lab.name)}
                                    </span>
                                  </div>
                                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                    {lab.paper_count && lab.paper_count > 0 && (
                                      <Tag color="green">{lab.paper_count} papers</Tag>
                                    )}
                                    <Button 
                                      type="text" 
                                      size="small"
                                      icon={isExpanded ? <CompressOutlined /> : <ExpandAltOutlined />}
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        handleCardClick(lab);
                                      }}
                                    />
                                    <Dropdown
                                      menu={{ 
                                        items: getLabActions(lab),
                                        onClick: ({ domEvent }) => {
                                          domEvent?.stopPropagation();
                                        }
                                      }}
                                      trigger={['click']}
                                    >
                                      <Button 
                                        type="text" 
                                        size="small"
                                        icon={<MoreOutlined />}
                                        onClick={(e) => e.stopPropagation()}
                                      />
                                    </Dropdown>
                                  </div>
                                </div>
                              }
                              style={{ 
                                height: isExpanded ? 'auto' : '400px',
                                cursor: 'pointer',
                                border: isExpanded ? '2px solid #1890ff' : '1px solid #d9d9d9',
                                transition: 'all 0.3s ease'
                              }}
                              onClick={() => handleCardClick(lab)}
                              hoverable
                            >
                              {isExpanded ? (
                                // Expanded view
                                <div>
                                  <Row gutter={[24, 16]}>
                                    <Col span={12}>
                                      <Card title="Lab Information" size="small">
                                        <Space direction="vertical" style={{ width: '100%' }}>
                                          <div>
                                            <strong>Principal Investigator:</strong>
                                            <div style={{ marginTop: 4 }}>
                                              <Avatar size="small" style={{ backgroundColor: '#52c41a', marginRight: 8 }}>
                                                <TeamOutlined />
                                              </Avatar>
                                              {lab.pi}
                                            </div>
                                          </div>
                                          
                                          <div>
                                            <strong>Institution:</strong>
                                            <div style={{ marginTop: 4 }}>{lab.institution}</div>
                                          </div>
                                          
                                          <div>
                                            <strong>Location:</strong>
                                            <div style={{ marginTop: 4 }}>
                                              <GlobalOutlined style={{ marginRight: 8 }} />
                                              {lab.city}, {lab.country}
                                            </div>
                                          </div>
                                          
                                          {lab.established_year && (
                                            <div>
                                              <strong>Established:</strong>
                                              <div style={{ marginTop: 4 }}>
                                                <CalendarOutlined style={{ marginRight: 8 }} />
                                                {lab.established_year}
                                              </div>
                                            </div>
                                          )}
                                          
                                          {lab.description && (
                                            <div>
                                              <strong>Description:</strong>
                                              <div style={{ marginTop: 4, padding: 8, background: '#f5f5f5', borderRadius: 4 }}>
                                                {lab.description}
                                              </div>
                                            </div>
                                          )}
                                          
                                          <div style={{ display: 'flex', gap: 8 }}>
                                            {lab.website && (
                                              <Button 
                                                type="primary"
                                                href={lab.website} 
                                                target="_blank"
                                                icon={<LinkOutlined />}
                                                onClick={(e) => e.stopPropagation()}
                                              >
                                                Visit Lab
                                              </Button>
                                            )}
                                          </div>
                                        </Space>
                                      </Card>
                                    </Col>
                                    
                                    <Col span={12}>
                                      <Card title="Research Focus" size="small">
                                        {lab.focus_areas && lab.focus_areas.length > 0 ? (
                                          <div>
                                            {lab.focus_areas.map((area, index) => (
                                              <Tag key={index} color="geekblue" style={{ marginBottom: 4 }}>
                                                {area}
                                              </Tag>
                                            ))}
                                          </div>
                                        ) : (
                                          <div style={{ color: '#999' }}>No focus areas specified</div>
                                        )}
                                        
                                        {lab.funding_sources && lab.funding_sources.length > 0 && (
                                          <div style={{ marginTop: 16 }}>
                                            <strong>Funding Sources:</strong>
                                            <div style={{ marginTop: 8 }}>
                                              {lab.funding_sources.map((source, index) => (
                                                <Tag key={index} color="orange" style={{ marginBottom: 4 }}>
                                                  <DollarOutlined style={{ marginRight: 4 }} />
                                                  {source}
                                                </Tag>
                                              ))}
                                            </div>
                                          </div>
                                        )}
                                      </Card>
                                    </Col>
                                  </Row>
                                  
                                  {lab.papers && lab.papers.length > 0 && (
                                    <Card title={`Recent Papers (${lab.papers.length})`} style={{ marginTop: 16 }} size="small">
                                      <List
                                        itemLayout="vertical"
                                        dataSource={lab.papers}
                                        renderItem={(paper, index) => (
                                          <List.Item
                                            key={index}
                                            actions={[
                                              paper.pdf_url && (
                                                <Button 
                                                  type="link" 
                                                  href={paper.pdf_url}
                                                  target="_blank"
                                                  onClick={(e) => e.stopPropagation()}
                                                  icon={<FileTextOutlined />}
                                                >
                                                  PDF
                                                </Button>
                                              ),
                                              paper.arxiv_id && (
                                                <Button 
                                                  type="link" 
                                                  href={`https://arxiv.org/abs/${paper.arxiv_id}`}
                                                  target="_blank"
                                                  onClick={(e) => e.stopPropagation()}
                                                  icon={<LinkOutlined />}
                                                >
                                                  ArXiv
                                                </Button>
                                              )
                                            ].filter(Boolean)}
                                          >
                                            <List.Item.Meta
                                              title={
                                                <div style={{ fontSize: '14px', fontWeight: 'bold' }}>
                                                  {paper.title}
                                                </div>
                                              }
                                              description={
                                                <div>
                                                  <div style={{ marginBottom: 4 }}>
                                                    <strong>Authors:</strong> {formatAuthors(paper.authors)}
                                                  </div>
                                                  {paper.venue && (
                                                    <div style={{ marginBottom: 4 }}>
                                                      <strong>Venue:</strong> {paper.venue}
                                                    </div>
                                                  )}
                                                  {paper.publication_date && (
                                                    <div style={{ marginBottom: 4 }}>
                                                      <strong>Date:</strong> {new Date(paper.publication_date).toLocaleDateString()}
                                                    </div>
                                                  )}
                                                  {paper.abstract && (
                                                    <div style={{ marginTop: 8, padding: 8, background: '#f9f9f9', borderRadius: 4 }}>
                                                      <strong>Abstract:</strong> {paper.abstract.length > 300 ? paper.abstract.substring(0, 300) + '...' : paper.abstract}
                                                    </div>
                                                  )}
                                                </div>
                                              }
                                            />
                                          </List.Item>
                                        )}
                                      />
                                    </Card>
                                  )}
                                </div>
                              ) : (
                                // Collapsed view
                                <div style={{ height: '340px', overflowY: 'auto' }}>
                                  <p><strong>PI:</strong> {lab.pi}</p>
                                  <p><strong>Institution:</strong> {
                                    lab.institution.length > 25 ? 
                                    lab.institution.substring(0, 25) + '...' : 
                                    lab.institution
                                  }</p>
                                  <p><strong>Location:</strong> {lab.city}, {lab.country}</p>
                                  
                                  {lab.focus_areas && lab.focus_areas.length > 0 && (
                                    <div style={{ marginTop: 8 }}>
                                      <strong>Focus:</strong>
                                      <div style={{ marginTop: 4 }}>
                                        {lab.focus_areas.slice(0, 2).map((area, index) => (
                                          <Tag key={index} color="geekblue" style={{ marginBottom: 4 }}>
                                            {area.length > 12 ? area.substring(0, 12) + '...' : area}
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
                                  
                                  {lab.papers && lab.papers.length > 0 && (
                                    <div style={{ marginTop: 12 }}>
                                      <Divider style={{ margin: '8px 0' }}>Recent Papers</Divider>
                                      {lab.papers.slice(0, 2).map((paper, index) => (
                                        <div key={index} className="paper-item" style={{ marginBottom: 8, padding: 6, background: '#f9f9f9', borderRadius: 4 }}>
                                          <Tooltip title={paper.title}>
                                            <div style={{ fontWeight: 'bold', fontSize: '12px', marginBottom: 2 }}>
                                              {paper.title.length > 60 ? paper.title.substring(0, 60) + '...' : paper.title}
                                            </div>
                                          </Tooltip>
                                          <div style={{ fontSize: '11px', color: '#666' }}>
                                            {paper.venue && (
                                              <span>{paper.venue} • </span>
                                            )}
                                            {paper.publication_date && (
                                              <span>{new Date(paper.publication_date).getFullYear()}</span>
                                            )}
                                          </div>
                                          {(paper.pdf_url || paper.arxiv_id) && (
                                            <Button 
                                              type="link" 
                                              size="small"
                                              href={paper.pdf_url || `https://arxiv.org/abs/${paper.arxiv_id}`}
                                              target="_blank"
                                              onClick={(e) => e.stopPropagation()}
                                              style={{ padding: 0, height: 'auto', fontSize: '11px' }}
                                            >
                                              View PDF →
                                            </Button>
                                          )}
                                        </div>
                                      ))}
                                      {lab.papers.length > 2 && (
                                        <div style={{ textAlign: 'center', fontSize: '12px', color: '#666' }}>
                                          +{lab.papers.length - 2} more papers (click to expand)
                                        </div>
                                      )}
                                    </div>
                                  )}
                                  
                                  {lab.website && (
                                    <div style={{ position: 'absolute', bottom: 8, left: 16, right: 16 }}>
                                      <Button 
                                        type="link" 
                                        size="small"
                                        href={lab.website} 
                                        target="_blank"
                                        onClick={(e) => e.stopPropagation()}
                                        style={{ padding: 0 }}
                                        icon={<LinkOutlined />}
                                      >
                                        Visit Lab
                                      </Button>
                                    </div>
                                  )}
                                </div>
                              )}
                            </Card>
                          </Col>
                        );
                      })}
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

      <Modal
        title="Scrape Latest Papers"
        open={scrapeModalVisible}
        onOk={handleScrapePapers}
        onCancel={() => setScrapeModalVisible(false)}
        confirmLoading={scrapingInProgress}
        width={600}
      >
        <div style={{ marginBottom: 16 }}>
          <h4>Select Labs to Scrape:</h4>
          <div style={{ maxHeight: 200, overflowY: 'auto', border: '1px solid #d9d9d9', padding: 8 }}>
            <Checkbox
              indeterminate={selectedLabsForScraping.length > 0 && selectedLabsForScraping.length < labs.length}
              checked={selectedLabsForScraping.length === labs.length}
              onChange={(e) => {
                if (e.target.checked) {
                  setSelectedLabsForScraping(labs.map(lab => lab.id));
                } else {
                  setSelectedLabsForScraping([]);
                }
              }}
            >
              Select All ({labs.length} labs)
            </Checkbox>
            <Divider style={{ margin: '8px 0' }} />
            {labs.map(lab => (
              <div key={lab.id} style={{ marginBottom: 4 }}>
                <Checkbox
                  checked={selectedLabsForScraping.includes(lab.id)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedLabsForScraping([...selectedLabsForScraping, lab.id]);
                    } else {
                      setSelectedLabsForScraping(selectedLabsForScraping.filter(id => id !== lab.id));
                    }
                  }}
                >
                  {lab.name} {lab.paper_count ? `(${lab.paper_count} papers)` : '(no papers)'}
                </Checkbox>
              </div>
            ))}
          </div>
        </div>

        <div style={{ marginBottom: 16 }}>
          <h4>Select Sources:</h4>
          <Checkbox.Group
            value={scrapingSources}
            onChange={setScrapingSources}
          >
            <Space direction="vertical">
              <Checkbox value="arxiv">ArXiv (Academic Papers)</Checkbox>
              <Checkbox value="scholar">Google Scholar (Citations)</Checkbox>
              <Checkbox value="website">Lab Website (Recent Publications)</Checkbox>
            </Space>
          </Checkbox.Group>
        </div>

        <Alert
          message="Paper Scraping Info"
          description="This will scrape up to 5 recent papers per lab from the selected sources. The process may take a few minutes."
          type="info"
          showIcon
        />
      </Modal>

      <LabFormModal
        visible={labFormVisible}
        onCancel={() => setLabFormVisible(false)}
        onSuccess={handleLabFormSuccess}
        lab={currentLab}
        mode={formMode}
      />
    </Layout>
  );
};

export default App;